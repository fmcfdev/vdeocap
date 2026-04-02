import sys
import os
import shutil
import uuid
import time
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Configura o Python para encontrar os módulos na pasta 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.transcriber import Transcriber
from app.core.translator import Translator
from app.core.renderer import Renderer

# --- MÁQUINA DE FILA (WORKER) ---
fila_de_processamento = asyncio.Queue()

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 Megabytes
ALLOWED_EXTENSIONS = {"mp4", "mov", "webm"}

async def worker_de_video():
    """
    Trabalhador que fica rodando em segundo plano.
    Ele processa estritamente UM vídeo por vez, protegendo a CPU e a RAM.
    """
    while True:
        # Aguarda até que haja um vídeo na fila
        tarefa = await fila_de_processamento.get()
        video_path, task_id, idioma_dest, settings = tarefa
        
        try:
            # Roda o processamento pesado em uma thread separada para não travar o loop do FastAPI
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None, 
                processar_em_background, 
                video_path, task_id, idioma_dest, settings
            )
        except Exception as e:
            print(f"❌ Erro crítico no Worker: {e}")
        finally:
            # Sinaliza que a tarefa atual foi concluída, liberando o worker para pegar o próximo vídeo
            fila_de_processamento.task_done()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicia o worker em segundo plano quando a aplicação subir
    asyncio.create_task(worker_de_video())
    yield

# --- INICIALIZAÇÃO ---
# Adicionamos o lifespan para ligar o nosso worker junto com a API
app = FastAPI(title="Vdeocap API - SaaS Edition", lifespan=lifespan)

# Configuração de CORS para permitir a comunicação com o Next.js (Porta 3000)
origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estrutura de Pastas
UPLOAD_DIR = "storage/uploads"
OUTPUT_DIR = "storage/outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Motores (Singletons)
motor_transcricao = Transcriber(model_size="base")
motor_video = Renderer(output_folder=OUTPUT_DIR)

# Estado das tarefas
tarefas_status = {}

# --- FUNÇÕES DE UTILITÁRIO (HOUSEKEEPING) ---

async def remover_arquivo_depois_de_tempo(caminho: str, delay: int = 3600):
    """
    Remove o arquivo após o tempo determinado (padrão 1 hora).
    Usa asyncio.sleep para não travar a execução do servidor.
    """
    await asyncio.sleep(delay)
    if os.path.exists(caminho):
        try:
            os.remove(caminho)
            print(f"🔥 Limpeza SaaS: Arquivo removido para economizar espaço: {caminho}")
        except Exception as e:
            print(f"⚠️ Erro ao remover arquivo: {e}")

# --- ORQUESTRADOR DE IA ---

def processar_em_background(video_path: str, task_id: str, idioma_dest: str, settings: dict):
    try:
        # PASSO 1: Transcrição
        tarefas_status[task_id] = "Passo 1/3: Transcrevendo áudio com IA..."
        trechos_pt = motor_transcricao.transcribe(video_path)
        print(f">>>>>>>>>>>>>>>>>>>>>>> {trechos_pt} <<<<<<<<<<<<<<<<<<<<<<<")  # Debug: Mostra o texto total gerado pela transcrição

        # ---------------------------------------------------------
        # NOVA TRAVA RIGOROSA ANTIFANTASMA E ALUCINAÇÕES
        # ---------------------------------------------------------
        if not trechos_pt:
            tarefas_status[task_id] = "Erro: Nenhuma voz detectada no vídeo."
            return

        # Junta tudo separando por espaço
        texto_total = " ".join([segmento.get('text', '') for segmento in trechos_pt]).strip()
        palavras = texto_total.split()
        
        # Cria uma "lista negra" com alucinações comuns do Whisper em vídeos mudos
        alucinacoes_comuns = ["you", "you.", "i", "the", "obrigado", "obrigado."]

        # Se a IA achou 2 palavras ou menos (ex: "You"), OU se for exatamente uma alucinação conhecida
        if len(palavras) <= 2 or texto_total.lower().strip() in alucinacoes_comuns:
            tarefas_status[task_id] = "Erro: Áudio vazio ou falas insuficientes para gerar legenda."
            print(f"[Vdeocap] Processo cancelado: Fantasma do Whisper barrado ('{texto_total}')")
            return
        # ---------------------------------------------------------

        # PASSO 2: Tradução
        tarefas_status[task_id] = f"Passo 2/3: Traduzindo para {idioma_dest}..."
        motor_traducao = Translator(from_code="pt", to_code=idioma_dest)
        trechos_final = motor_traducao.translate_segments(trechos_pt)

        # PASSO 3: Renderização
        tarefas_status[task_id] = "Passo 3/3: Renderizando vídeo final (FFmpeg)..."
        ass_path = motor_video.generate_ass_file(trechos_final, settings, filename=f"{task_id}.ass")
        motor_video.burn_subtitles(video_path, ass_path, output_name=f"final_{task_id}.mp4")
        
        tarefas_status[task_id] = "Concluído"
        print(f"[Vdeocap] Sucesso: {task_id}")
        
    except Exception as e:
        erro_msg = str(e)
        
        # Intercepta o "tropeço" clássico do Whisper ao lidar com silêncio absoluto
        if "tuple index out of range" in erro_msg.lower() or "index out of bounds" in erro_msg.lower():
            tarefas_status[task_id] = "Erro: O vídeo não possui áudio ou a trilha sonora está vazia."
            print(f"[Vdeocap] Processo cancelado: Vídeo sem áudio detectado no Whisper ({task_id})")
        else:
            # Para outros erros desconhecidos
            tarefas_status[task_id] = f"Erro ao processar vídeo: {erro_msg}"
            print(f"[Vdeocap] Erro na tarefa {task_id}: {erro_msg}")

# --- ROTAS DA API ---

@app.post("/upload")
async def receber_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    idioma: str = Form("en"),
    tamanho_fonte: str = Form("media"),
    cor_fonte: str = Form("#FFFF00"),
    cor_fundo: str = Form("#000000"),
    formato_video: str = Form("horizontal")
):
    # 1. Validação de Segurança: Extensão do arquivo
    extensao = file.filename.split(".")[-1].lower()
    if extensao not in ALLOWED_EXTENSIONS:
        return {"error": "Formato não suportado. Use MP4, MOV ou WEBM."}

    task_id = str(uuid.uuid4())
    video_input_path = os.path.join(UPLOAD_DIR, f"{task_id}.{extensao}")
    video_output_path = os.path.join(OUTPUT_DIR, f"final_{task_id}.mp4")

    # 2. Validação de Segurança: Tamanho do Arquivo (Chunking)
    tamanho_total = 0
    with open(video_input_path, "wb") as buffer:
        # Lê o arquivo em pedaços de 1MB para não estourar a memória RAM
        while chunk := await file.read(1024 * 1024):
            tamanho_total += len(chunk)
            if tamanho_total > MAX_FILE_SIZE:
                # Se passar do limite, apaga o que já foi salvo e bloqueia
                os.remove(video_input_path)
                return {"error": "Arquivo muito grande. O limite máximo é 100MB."}
            buffer.write(chunk)

    # Configurações de Layout
    if formato_video == "vertical":
        res_x, res_y, margin_v = 1080, 1920, 450
        mapa_fontes = {"pequena": 50, "media": 80, "grande": 110}
    else:
        res_x, res_y, margin_v = 1920, 1080, 120
        mapa_fontes = {"pequena": 45, "media": 70, "grande": 95}

    configuracoes = {
        "font": "Arial Black",
        "fontsize": mapa_fontes.get(tamanho_fonte, 80),
        "color": cor_fonte,
        "bg_color": cor_fundo,
        "bg_opacity": 85,
        "margin_v": margin_v,
        "res_x": res_x,
        "res_y": res_y
    }

    # Envia para a fila
    await fila_de_processamento.put((video_input_path, task_id, idioma, configuracoes))
    tarefas_status[task_id] = "Na fila: Aguardando processamento..."
    
    # Agenda a limpeza (Proteção de Disco)
    background_tasks.add_task(remover_arquivo_depois_de_tempo, video_input_path, 3600)
    background_tasks.add_task(remover_arquivo_depois_de_tempo, video_output_path, 3600)
    
    return {"task_id": task_id}

@app.get("/status/{task_id}")
async def verificar_status(task_id: str):
    status_texto = tarefas_status.get(task_id)
    if not status_texto:
        return {"error": "Não encontrado", "status": "failed", "progress": 0}

    progress = 0
    tech_status = "processing"
    
    # Progressão atualizada para refletir o novo estado de fila
    if "Na fila" in status_texto: progress = 5
    elif "Passo 1" in status_texto: progress = 20
    elif "Passo 2" in status_texto: progress = 60
    elif "Passo 3" in status_texto: progress = 90
    elif status_texto == "Concluído":
        progress, tech_status = 100, "completed"
    elif "Erro" in status_texto:
        tech_status = "failed"

    return {
        "task_id": task_id,
        "status": tech_status,
        "message": status_texto,
        "progress": progress,
        "ready": (status_texto == "Concluído")
    }

@app.get("/download/{task_id}")
async def baixar_resultado(task_id: str):
    caminho_arquivo = os.path.join(OUTPUT_DIR, f"final_{task_id}.mp4")
    if os.path.exists(caminho_arquivo) and tarefas_status.get(task_id) == "Concluído":
        return FileResponse(caminho_arquivo, media_type="video/mp4", filename=f"vdeocap_{task_id}.mp4")
    return {"error": "Arquivo não disponível"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
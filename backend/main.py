import sys
import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Configura o Python para encontrar os módulos na pasta 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.transcriber import Transcriber
from app.core.translator import Translator
from app.core.renderer import Renderer

# Inicialização do App FastAPI
app = FastAPI(title="Vdeocap API - O Coração do seu Micro-SaaS")

# CONFIGURAÇÃO DE CORS: Crucial para que o Frontend (Next.js na porta 3000) 
# consiga fazer requisições para o Backend (FastAPI na porta 8000).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, substitua pelo domínio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estrutura de Pastas para Armazenamento Persistente
UPLOAD_DIR = "storage/uploads"
OUTPUT_DIR = "storage/outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Instanciação dos Motores (Padrão Singleton para economia de recursos)
motor_transcricao = Transcriber(model_size="base")
motor_video = Renderer(output_folder=OUTPUT_DIR)

# Rastreamento de Estado: Dicionário global que armazena o status de cada vídeo
tarefas_status = {} 

def processar_em_background(video_path: str, task_id: str, idioma_dest: str, settings: dict):
    """
    Orquestrador de Fluxo de Trabalho (Workflow).
    Executa os 3 passos fundamentais: Transcrição -> Tradução -> Renderização.
    """
    try:
        # PASSO 1: Transcrição
        tarefas_status[task_id] = "Passo 1/3: Transcrevendo áudio com IA..."
        trechos_pt = motor_transcricao.transcribe(video_path)

        # PASSO 2: Tradução e Fatiamento
        tarefas_status[task_id] = f"Passo 2/3: Traduzindo para {idioma_dest}..."
        motor_traducao = Translator(from_code="pt", to_code=idioma_dest)
        trechos_final = motor_traducao.translate_segments(trechos_pt)

        # PASSO 3: Renderização Final (Queima de Legenda)
        tarefas_status[task_id] = "Passo 3/3: Renderizando vídeo final (FFmpeg)..."
        ass_path = motor_video.generate_ass_file(trechos_final, settings, filename=f"{task_id}.ass")
        motor_video.burn_subtitles(video_path, ass_path, output_name=f"final_{task_id}.mp4")
        
        # Conclusão do Processo
        tarefas_status[task_id] = "Concluído"
        print(f"[Vdeocap] Sucesso: Tarefa {task_id} finalizada.")
        
    except Exception as e:
        tarefas_status[task_id] = f"Erro: {str(e)}"
        print(f"[Vdeocap] Erro Crítico na Tarefa {task_id}: {e}")

@app.get("/status/{task_id}")
async def verificar_status(task_id: str):
    """
    Endpoint de Polling: O Frontend consulta este endpoint para saber o progresso atual.
    """
    status_atual = tarefas_status.get(task_id, "ID não encontrado")
    is_ready = (status_atual == "Concluído")
    
    return {
        "task_id": task_id, 
        "status": status_atual,
        "ready": is_ready
    }

@app.post("/upload")
async def receber_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    idioma: str = Form("en"),
    tamanho_fonte: str = Form("media"),
    cor_fonte: str = Form("#FFFF00"),
    formato_video: str = Form("horizontal")
):
    """
    Ponto de Entrada Principal: Recebe o arquivo e os parâmetros de estilo.
    Valida as regras de negócio para formatos Vertical vs Horizontal.
    """
    task_id = str(uuid.uuid4())
    extensao = file.filename.split(".")[-1]
    video_path = os.path.join(UPLOAD_DIR, f"{task_id}.{extensao}")

    # Escrita do arquivo em disco (Streaming)
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # REGRAS DE OURO: Ajustes dinâmicos de layout baseados no formato
    if formato_video == "vertical":
        res_x, res_y = 1080, 1920
        margin_v = 450 # Protege contra a interface (likes/comentários) do TikTok/Reels
        mapa_fontes = {"pequena": 50, "media": 80, "grande": 110}
    else:
        res_x, res_y = 1920, 1080
        margin_v = 120 # Rodapé clássico para YouTube e Vídeos Tradicionais
        mapa_fontes = {"pequena": 45, "media": 70, "grande": 95}

    # Consolidação das Configurações de Estilo
    configuracoes = {
        "font": "Arial Black",
        "fontsize": mapa_fontes.get(tamanho_fonte, 80),
        "color": cor_fonte,
        "bg_color": "#000000",
        "bg_opacity": 85,
        "margin_v": margin_v,
        "res_x": res_x,
        "res_y": res_y
    }

    # Dispara o processamento assíncrono
    background_tasks.add_task(processar_em_background, video_path, task_id, idioma, configuracoes)
    
    tarefas_status[task_id] = "Upload recebido. Aguardando processamento..."
    
    return {"task_id": task_id, "status": "processando"}

@app.get("/download/{task_id}")
async def baixar_resultado(task_id: str):
    """
    Endpoint de Entrega: Só libera o arquivo se o status for estritamente "Concluído",
    evitando que o usuário baixe vídeos corrompidos ou incompletos.
    """
    caminho_arquivo = os.path.join(OUTPUT_DIR, f"final_{task_id}.mp4")
    status_atual = tarefas_status.get(task_id)
    
    if status_atual != "Concluído":
        return {
            "status": "Em processamento", 
            "detalhe": status_atual,
            "task_id": task_id
        }

    if os.path.exists(caminho_arquivo):
        return FileResponse(
            caminho_arquivo, 
            media_type="video/mp4", 
            filename=f"vdeocap_{task_id}.mp4"
        )
    
    return {"status": "Erro", "mensagem": "Arquivo não encontrado."}

if __name__ == "__main__":
    import uvicorn
    # Inicialização do servidor Uvicorn (Host 0.0.0.0 permite acesso na rede local)
    uvicorn.run(app, host="0.0.0.0", port=8000)
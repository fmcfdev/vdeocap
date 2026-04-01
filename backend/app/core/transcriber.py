from faster_whisper import WhisperModel

class Transcriber:
    """
    Motor de Transcrição do Vdeocap.
    Utiliza o modelo Faster-Whisper para converter áudio em texto com alta precisão
    e extrair o tempo exato de cada palavra (timestamps).
    """
    def __init__(self, model_size="base", device="cpu"):
        # Inicializa o modelo Whisper. 
        # model_size: "base" é um ótimo equilíbrio entre velocidade e precisão.
        # compute_type: "int8" permite rodar em CPUs comuns sem consumir toda a memória.
        self.model = WhisperModel(model_size, device=device, compute_type="int8")

    def transcribe(self, video_path):
        """
        Analisa o arquivo de vídeo e retorna uma lista de segmentos estruturados.
        Cada segmento contém o texto completo e os metadados de tempo de cada palavra.
        """
        # word_timestamps=True: Essencial para o Vdeocap conseguir fatiar legendas longas depois.
        # beam_size=5: Melhora a precisão da transcrição ao analisar múltiplas possibilidades de frases.
        segments, info = self.model.transcribe(
            video_path, 
            beam_size=5, 
            word_timestamps=True
        )

        results = []
        for segment in segments:
            # Estruturamos os dados para facilitar o trabalho do tradutor e do renderizador
            results.append({
                "start": segment.start, # Início da frase em segundos
                "end": segment.end,     # Fim da frase em segundos
                "text": segment.text.strip(),
                "words": [
                    {
                        "start": w.start, 
                        "end": w.end, 
                        "word": w.word.strip()
                    } for w in segment.words
                ]
            })
            
        # O retorno é uma lista de dicionários pronta para ser processada pelo motor de tradução
        return results
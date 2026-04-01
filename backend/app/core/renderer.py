import os
import subprocess

class Renderer:
    """
    Motor de Renderização do Vdeocap.
    Responsável por gerar arquivos de legenda (.ass) e fundi-los ao vídeo usando FFmpeg.
    """
    def __init__(self, output_folder="storage/outputs"):
        self.output_folder = output_folder
        # Garante que a pasta de saída exista para evitar erros de I/O
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def _format_time(self, seconds):
        """
        Converte segundos puros para o formato de tempo exigido pelo ASS (H:MM:SS.cc).
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centiseconds = int((seconds - int(seconds)) * 100)
        return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"

    def _convert_color_to_ass(self, hex_color, opacity_percent):
        """
        Converte cores Hexadecimais (#RRGGBB) para o formato decimal do ASS (&HAAABBBGGG).
        Também calcula a opacidade (Alpha) para o fundo da legenda.
        """
        hex_color = hex_color.lstrip('#')
        r, g, b = hex_color[0:2], hex_color[2:4], hex_color[4:6]
        # Calcula o valor Alpha (transparência invertida: 0 é opaco, 255 é transparente)
        alpha_val = int(255 * (1 - (opacity_percent / 100)))
        alpha_hex = f"{alpha_val:02X}"
        return f"&H{alpha_hex}{b}{g}{r}"

    def generate_ass_file(self, segments, options, filename="subtitles.ass"):
        """
        Cria o arquivo de legenda Advanced Substation Alpha (.ass).
        Aplica os estilos de "Padrão Ouro": Padding, Spacing e Resolução Dinâmica.
        """
        path = os.path.join(self.output_folder, filename)
        
        # Processamento de cores dinâmicas vindas da API do Vdeocap
        primary_color = self._convert_color_to_ass(options.get('color', '#FFFFFF'), 100)
        back_color = self._convert_color_to_ass(options.get('bg_color', '#000000'), options.get('bg_opacity', 80))
        
        # Extração de configurações de estilo
        font_name = options.get('font', 'Arial Black')
        font_size = options.get('fontsize', 80)
        margin_v = options.get('margin_v', 450)
        res_x = options.get('res_x', 1080)
        res_y = options.get('res_y', 1920)
        
        # Estilização Avançada (UX Premium)
        outline_padding = 12  # Cria o "respiro" dentro da caixa preta
        spacing = 2          # Espaçamento entre letras para facilitar leitura rápida

        # Cabeçalho do arquivo ASS com as definições de estilo
        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {res_x}
PlayResY: {res_y}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Custom,{font_name},{font_size},{primary_color},&H000000FF,&H00000000,{back_color},1,0,0,0,100,100,{spacing},0,3,{outline_padding},0,2,100,100,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(header)
            for s in segments:
                start = self._format_time(s['start'])
                end = self._format_time(s['end'])
                # Sanitização de texto: remove quebras de linha para manter o layout da caixa
                text = s['text'].replace("\n", " ").strip()
                f.write(f"Dialogue: 0,{start},{end},Custom,,0,0,0,,{text}\n")
        
        return path

    def burn_subtitles(self, video_input, ass_path, output_name="video_final.mp4"):
        """
        Usa o FFmpeg para realizar o "Hard Burn" (fusão definitiva) da legenda no vídeo.
        Configurado para alta qualidade (CRF 18) e processamento rápido.
        """
        output_path = os.path.join(self.output_folder, output_name)
        
        # Ajuste de caminho para o filtro de legendas do FFmpeg (escapando caracteres especiais)
        ass_path_fixed = ass_path.replace("\\", "/").replace(":", "\\:")
        
        command = [
            'ffmpeg', '-y', '-i', video_input, 
            '-vf', f"subtitles='{ass_path_fixed}'", 
            '-c:v', 'libx264', 
            '-crf', '18',           # CRF baixo = Maior qualidade visual
            '-preset', 'veryfast',   # Equilíbrio entre velocidade e compressão
            '-c:a', 'copy',          # Copia o áudio original sem re-encodificar (perda zero)
            output_path
        ]
        
        # Executa o processo externo do FFmpeg
        subprocess.run(command, check=True)
        return output_path
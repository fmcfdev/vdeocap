import argostranslate.package
import argostranslate.translate
import os

class Translator:
    """
    Motor de Tradução e Fatiamento do Vdeocap.
    Responsável por traduzir textos offline e garantir que frases longas 
    sejam divididas em pedaços menores para não estourarem a tela do vídeo.
    """
    def __init__(self, from_code="pt", to_code="en"):
        self.from_code = from_code
        self.to_code = to_code
        
        # SÓ tenta instalar pacotes se as línguas forem DIFERENTES (Bypass para idioma original)
        if self.from_code != self.to_code:
            self._ensure_package_installed()

    def _ensure_package_installed(self):
        """
        Gerencia a instalação automática de pacotes de tradução offline.
        Busca no índice do Argos Translate e instala o par de idiomas necessário.
        """
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        
        # Procura o pacote específico (Ex: pt -> en)
        package_to_install = next(
            filter(
                lambda x: x.from_code == self.from_code and x.to_code == self.to_code,
                available_packages
            ), None
        )

        if package_to_install:
            installed_packages = argostranslate.package.get_installed_packages()
            is_already_installed = any(
                pkg.from_code == self.from_code and pkg.to_code == self.to_code 
                for pkg in installed_packages
            )

            if not is_already_installed:
                print(f"[Vdeocap] Baixando pacote de tradução: {self.from_code} -> {self.to_code}...")
                download_path = package_to_install.download()
                argostranslate.package.install_from_path(download_path)
        else:
            # Se o par de idiomas não existir, o sistema avisa o erro de suporte
            raise Exception(f"Tradução de {self.from_code} para {self.to_code} não é suportada offline.")

    def translate_segments(self, segments):
        """
        Processa a lista de segmentos: traduz o conteúdo e aplica a lógica de 
        fatiamento temporal (Slicing) para manter a legibilidade das legendas.
        """
        print(f"[Vdeocap] Processando {len(segments)} sentenças ({self.from_code} -> {self.to_code})")
        final_chunks = []

        for seg in segments:
            # 1. Obtenção do texto (Tradução ou Texto Original)
            if self.from_code == self.to_code:
                full_text = seg["text"]
            else:
                # Tradução offline com contexto de frase completa
                full_text = argostranslate.translate.translate(
                    seg["text"], self.from_code, self.to_code
                )
            
            # 2. Lógica de Fatiamento Inteligente
            # Se a tradução tiver 35 caracteres ou menos, mantemos em um único bloco
            if len(full_text) <= 35:
                final_chunks.append({
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": full_text
                })
            else:
                # Se for longa, dividimos a frase ao meio (mid)
                words = full_text.split()
                mid = len(words) // 2
                
                # Sincronizamos o tempo do corte usando a lista de 'words' original do Transcriber
                # Isso garante que a legenda mude exatamente quando a palavra é dita no áudio.
                time_split_index = min(mid, len(seg["words"]) - 1)
                split_time = seg["words"][time_split_index]["end"]

                # Parte A da Legenda
                final_chunks.append({
                    "start": seg["start"],
                    "end": split_time,
                    "text": " ".join(words[:mid])
                })
                
                # Parte B da Legenda
                final_chunks.append({
                    "start": split_time,
                    "end": seg["end"],
                    "text": " ".join(words[mid:])
                })

        return final_chunks
# 🎬 Vdeocap - Video Captioning & Translation AI

O Vdeocap é uma API de micro-serviço poderosa para automação de legendas e tradução de vídeos. Ele utiliza Inteligência Artificial de ponta para transformar áudio em texto, traduzir contextos e renderizar vídeos prontos para redes sociais (Reels, TikTok, YouTube).

---

## 🚀 Funcionalidades

- Transcrição Precisa: Utiliza o Faster-Whisper para extração de fala com timestamps por palavra.
- Tradução Offline: Motores do Argos Translate garantem privacidade e custo zero de API.
- Renderização Automática: Integração com FFmpeg para "Hard Burn" de legendas com estilo customizável.
- Fatiamento Inteligente: Algoritmo que quebra frases longas em blocos legíveis para vídeos curtos.
- Suporte Vertical/Horizontal: Ajuste automático de margens e fontes para diferentes formatos.

---

## 🛠️ Tecnologias Utilizadas

- Linguagem: Python 3.11+ (Suporta 3.13 com builds binários)
- Framework Web: FastAPI
- Processamento de Áudio: Faster-Whisper (IA)
- Tradução: Argos Translate (Open Source)
- Processamento de Vídeo: FFmpeg

---

## 📦 Como Rodar a API (Backend)

### 1. Pré-requisitos

Certifique-se de ter o FFmpeg instalado no seu sistema e adicionado ao seu PATH.

### 2. Configuração do Ambiente

Navegue até a pasta do backend:
cd backend

Crie e ative seu ambiente virtual:
python -m venv venv
source venv/Scripts/activate # No Windows (Git Bash)

### 3. Instalação de Dependências (Segura)

Para evitar erros de compilação em versões novas do Python, utilize o comando:
python -m pip install --upgrade pip
pip install --only-binary=:all: -r requirements.txt

### 4. Iniciando o Servidor

python main.py

A API estará disponível em http://127.0.0.1:8000.
Documentação interativa (Swagger): http://127.0.0.1:8000/docs

---

## 📄 Licença

Distribuído sob a licença MIT.

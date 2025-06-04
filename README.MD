🎥 AutoSub Translator

Este projeto é uma pipeline completa que transforma vídeos em conteúdos legendados automaticamente, com suporte para transcrição, tradução e inserção de legendas no vídeo.

✅ Funcionalidades

🎿 Extração de áudio de vídeos .mp4

🧠 Transcrição automática com OpenAI Whisper

🌍 Tradução opcional para outros idiomas (via googletrans)

📝 Geração de legendas no formato .srt

🖼️ Renderização de legendas como imagens com tipografia customizada

📽️ Exportação de vídeo com legendas embutidas (hardcoded)

📆 Requisitos

Python 3.8+

ffmpeg (instalado no sistema)

Instalar dependências

pip install -r requirements.txt

Dependências principais:

moviepy

openai-whisper

pysrt

googletrans==4.0.0rc1

Pillow

torch

🚀 Como Usar

Coloque seu vídeo .mp4 na pasta desejada

Rode o script principal:

python main.py

Informe o idioma original do vídeo (pt, en, etc.)

As legendas serão geradas automaticamente em:

output/video.srt (original)

output/video_translated.srt (traduzido, se desejar)

Os vídeos legendados são exportados para:

output/legendado_original.mp4

output/legendado_traduzido.mp4

📁 Estrutura

.
├── main.py
├── fonts/
│   └── Arial.ttf
├── output/
│   ├── audio.mp3
│   ├── video.srt
│   ├── video_translated.srt
│   ├── legendado_original.mp4
│   └── legendado_traduzido.mp4

🚰 Personalização

Fonte das legendas: edite font_path no script

Tamanho e cor: fontsize, text_color, stroke_color

Idioma da transcrição: language = 'pt', 'en', etc.

Tradução automática: altere target_language = 'en', 'es', etc.

🧐 Créditos

Transcrição: Whisper

Tradução: googletrans

Renderização: Pillow

Edição de vídeo: MoviePy

📄 Licença

Este projeto é de uso livre para fins educacionais e não comerciais.
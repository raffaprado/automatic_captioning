import os
import whisper
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
import pysrt
from datetime import timedelta
from googletrans import Translator
from PIL import Image, ImageDraw, ImageFont
import numpy as np


def extract_audio(video_path, audio_output_path):
    try:
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_output_path, codec='mp3')
        print(f"Áudio extraído para: {audio_output_path}")
        return True
    except Exception as e:
        print(f"Erro ao extrair áudio: {e}")
        return False


def transcribe_audio_with_local_model(audio_path, language="pt"):
    try:
        print(f"Iniciando transcrição com Whisper para o idioma: {language}...")
        model = whisper.load_model("small")
        print("Modelo Whisper carregado.")

        result = model.transcribe(audio_path, language=language)

        segments_data = []
        full_text = ""
        if "segments" in result:
            for segment in result["segments"]:
                segments_data.append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"].strip()
                })
                full_text += segment["text"].strip() + " "
        elif "text" in result:
            video_duration = VideoFileClip(audio_path).duration
            segments_data.append({
                "start": 0.0,
                "end": video_duration,
                "text": result["text"].strip()
            })
            full_text = result["text"].strip()

        return full_text, segments_data
    except Exception as e:
        print(f"Erro ao transcrever áudio com Whisper: {e}")
        print("Verifique FFmpeg e a disponibilidade do modelo Whisper. Tente 'pip install -U openai-whisper'.")
        return None, None


def create_srt_from_segments(segments, output_srt_path):
    subs = pysrt.SubRipFile()
    if not segments:
        print("Nenhum segmento de texto para criar legendas.")
        return

    for idx, segment in enumerate(segments):
        start_seconds = segment["start"]
        end_seconds = segment["end"]
        text = segment["text"]

        start_td = timedelta(seconds=start_seconds)
        end_td = timedelta(seconds=end_seconds)

        # Arredondando para milissegundos corretamente
        start_time_pysrt = pysrt.SubRipTime(
            hours=int(start_td.total_seconds() // 3600),
            minutes=int((start_td.total_seconds() % 3600) // 60),
            seconds=int(start_td.total_seconds() % 60),
            milliseconds=int((start_td.total_seconds() * 1000) % 1000)
        )

        end_time_pysrt = pysrt.SubRipTime(
            hours=int(end_td.total_seconds() // 3600),
            minutes=int((end_td.total_seconds() % 3600) // 60),
            seconds=int(end_td.total_seconds() % 60),
            milliseconds=int((end_td.total_seconds() * 1000) % 1000)
        )

        subs.append(pysrt.SubRipItem(index=idx + 1,
                                     start=start_time_pysrt,
                                     end=end_time_pysrt,
                                     text=text))

    subs.save(output_srt_path, encoding='utf-8')
    print(f"Arquivo SRT criado: {output_srt_path}")


def translate_text(text, target_language='en'):
    translator = Translator()
    try:
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        print(f"Erro ao traduzir texto: {e}")
        return None


def time_to_seconds(time_obj):
    return time_obj.hours * 3600 + time_obj.minutes * 60 + time_obj.seconds + time_obj.milliseconds / 1000


def create_text_image(text, font_path, fontsize, text_color, img_width, outline_color='black', outline_width=2):
    try:
        font = ImageFont.truetype(font_path, fontsize)
    except IOError:
        print(f"Aviso: Fonte '{font_path}' não encontrada. Usando fonte padrão.")
        font = ImageFont.load_default()

    lines = []
    if text.strip():
        words = text.split(' ')
        current_line_words = []
        for word in words:
            test_line = ' '.join(current_line_words + [word])
            bbox = ImageDraw.Draw(Image.new('RGBA', (1, 1))).textbbox((0, 0), test_line, font=font)
            text_w = bbox[2] - bbox[0]

            if text_w < img_width * 0.9:
                current_line_words.append(word)
            else:
                lines.append(' '.join(current_line_words))
                current_line_words = [word]
        if current_line_words:
            lines.append(' '.join(current_line_words))
    else:
        lines = [""]

    text_height = 0
    for line in lines:
        bbox = ImageDraw.Draw(Image.new('RGBA', (1, 1))).textbbox((0, 0), line, font=font)
        text_height += (bbox[3] - bbox[1])

    padding_y = 20
    img = Image.new('RGBA', (img_width, text_height + padding_y), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    y_offset = padding_y / 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        x_offset = (img_width - line_width) / 2

        # Desenha a borda
        for x_outline in range(-outline_width, outline_width + 1):
            for y_outline in range(-outline_width, outline_width + 1):
                draw.text((x_offset + x_outline, y_offset + y_outline), line, font=font, fill=outline_color)

        # Desenha o texto principal
        draw.text((x_offset, y_offset), line, font=font, fill=text_color)

        y_offset += (bbox[3] - bbox[1])

    return img


def add_subtitles_to_video(video_path, srt_path, output_video_path, font_name='Arial.ttf', fontsize=50,
                           text_color='white',
                           bg_color='black', position=('center', 'bottom'), outline_color='black', outline_width=3):
    try:
        video = VideoFileClip(video_path)
        subtitles = pysrt.open(srt_path, encoding='utf-8')

        subtitle_clips = []
        video_width, video_height = video.size

        font_file_path = font_name
        if not os.path.exists(font_file_path) or not font_file_path.lower().endswith(".ttf"):
            font_file_path_check = font_file_path if font_file_path.lower().endswith(
                ".ttf") else font_file_path + ".ttf"
            found_font = False
            common_font_paths = [
                f"C:/Windows/Fonts/{font_file_path_check}",
                f"C:/Windows/Fonts/{font_file_path_check.lower()}",
                f"C:/Windows/Fonts/{font_file_path_check.upper()}",
                os.path.join(os.path.dirname(__file__), font_file_path_check)
            ]
            for path in common_font_paths:
                if os.path.exists(path):
                    font_file_path = path
                    found_font = True
                    break

            if not found_font:
                print(f"Aviso: Fonte '{font_name}' (ou '{font_file_path_check}') não encontrada. Usando fonte padrão.")
                font_file_path = font_name

        for sub in subtitles:
            start_time = time_to_seconds(sub.start)
            end_time = time_to_seconds(sub.end)
            duration = end_time - start_time

            text_image = create_text_image(
                sub.text,
                font_file_path,
                fontsize,
                text_color,
                int(video_width * 0.9),  # Largura da imagem do texto
                outline_color=outline_color,
                outline_width=outline_width
            )

            text_clip = ImageClip(np.array(text_image)).set_start(start_time).set_duration(duration)

            if isinstance(position, tuple):
                text_position = position
            elif position == 'bottom':
                text_position = ('center', video_height * 0.85)
            elif position == 'top':
                text_position = ('center', video_height * 0.05)
            else:
                text_position = ('center', 'bottom')

            subtitle_clips.append(text_clip.set_position(text_position))

        final_video = CompositeVideoClip([video] + subtitle_clips)
        final_video.write_videofile(output_video_path, codec='libx264', audio_codec='aac')
        print(f"Vídeo com legendas salvo em: {output_video_path}")
    except Exception as e:
        print(f"Erro ao adicionar legendas ao vídeo: {e}")


if __name__ == "__main__":
    video_input_path = "C:/Users/Rafae/Desktop/video/baixado/teste.mp4"
    audio_output_path = "extracted_audio.mp3"

    print("\n--- Configuração de Idioma ---")
    print(
        "Códigos de idioma comuns: pt (Português), en (Inglês), es (Espanhol), fr (Francês), de (Alemão), it (Italiano).")

    IDIOMA_BASE = input("Digite o idioma base do vídeo (ex: pt): ").strip().lower()
    while not IDIOMA_BASE:
        IDIOMA_BASE = input("O idioma base não pode ser vazio. Digite novamente: ").strip().lower()

    IDIOMA_TRADUCAO = input(
        "Digite o idioma para traduzir (ou deixe em branco e pressione Enter para pular a tradução): ").strip().lower()
    if not IDIOMA_TRADUCAO:
        IDIOMA_TRADUCAO = None
    elif IDIOMA_TRADUCAO == IDIOMA_BASE:
        print("O idioma de tradução é o mesmo do idioma base. A tradução será pulada.")
        IDIOMA_TRADUCAO = None

    print(f"\nIdioma Base Selecionado: {IDIOMA_BASE.upper()}")
    if IDIOMA_TRADUCAO:
        print(f"Idioma de Tradução Selecionado: {IDIOMA_TRADUCAO.upper()}")
    else:
        print("Tradução desativada.")
    print("---------------------------\n")

    srt_base_path = f"subtitles_{IDIOMA_BASE}.srt"
    video_output_base = f"C:/Users/Rafae/Desktop/video/editado/video_com_legendas_{IDIOMA_BASE}.mp4"

    srt_traducao_path = f"subtitles_{IDIOMA_TRADUCAO}.srt" if IDIOMA_TRADUCAO else None
    video_output_traducao = f"C:/Users/Rafae/Desktop/video/editado/video_com_legendas_{IDIOMA_TRADUCAO}.mp4" if IDIOMA_TRADUCAO else None

    if extract_audio(video_input_path, audio_output_path):
        full_transcribed_text, segments_base = transcribe_audio_with_local_model(audio_output_path,
                                                                                 language=IDIOMA_BASE)

        if full_transcribed_text and segments_base is not None:  # Verifica se segments_base não é None
            print(f"\nTranscrição em {IDIOMA_BASE.upper()}:")
            print(full_transcribed_text[:500] + "...")

            create_srt_from_segments(segments_base, srt_base_path)
            add_subtitles_to_video(video_input_path, srt_base_path, video_output_base,
                                   font_name='arial.ttf', fontsize=50, text_color='white',
                                   outline_color='black', outline_width=3)

            if IDIOMA_TRADUCAO:
                translated_text = translate_text(full_transcribed_text, target_language=IDIOMA_TRADUCAO)
                if translated_text:
                    print(f"\nTradução para {IDIOMA_TRADUCAO.upper()}:")
                    print(translated_text[:500] + "...")

                    # Para a legenda traduzida, precisamos re-segmentar o texto traduzido
                    # com base na duração dos segmentos originais.
                    # Isso é uma estimativa, pois a API do googletrans não fornece timestamps.
                    translated_segments = []

                    # Divide o texto traduzido em palavras para distribuição
                    translated_words = translated_text.split()
                    total_translated_words = len(translated_words)

                    # Calcular a duração total dos segmentos originais
                    total_original_duration = segments_base[-1]['end'] if segments_base else 0

                    current_word_index = 0
                    for segment in segments_base:
                        segment_duration = segment['end'] - segment['start']

                        # Estimar quantas palavras traduzidas para este segmento
                        # Proporção da duração do segmento em relação à duração total
                        if total_original_duration > 0:
                            word_count_for_segment = int(
                                (segment_duration / total_original_duration) * total_translated_words)
                            if word_count_for_segment == 0 and total_translated_words > 0:  # Garante pelo menos uma palavra para segmentos curtos
                                word_count_for_segment = 1
                        else:
                            word_count_for_segment = 0

                        # Garante que não exceda o número total de palavras
                        if current_word_index + word_count_for_segment > total_translated_words:
                            word_count_for_segment = total_translated_words - current_word_index

                        segment_translated_text = " ".join(
                            translated_words[current_word_index: current_word_index + word_count_for_segment])

                        translated_segments.append({
                            "start": segment["start"],
                            "end": segment["end"],
                            "text": segment_translated_text
                        })
                        current_word_index += word_count_for_segment

                    # Se sobrar texto traduzido (devido a arredondamentos), anexa ao último segmento
                    if current_word_index < total_translated_words and translated_segments:
                        translated_segments[-1]['text'] += " " + " ".join(translated_words[current_word_index:])

                    create_srt_from_segments(translated_segments, srt_traducao_path)
                    add_subtitles_to_video(video_input_path, srt_traducao_path, video_output_traducao,
                                           font_name='arial.ttf', fontsize=50, text_color='lightblue',
                                           outline_color='black', outline_width=3)
                else:
                    print(f"Não foi possível traduzir para {IDIOMA_TRADUCAO.upper()}.")
            else:
                print("Nenhum idioma de tradução definido. Pulando a etapa de tradução.")

        else:
            print(f"Não foi possível transcrever o áudio em {IDIOMA_BASE.upper()}.")
    else:
        print("Não foi possível extrair o áudio do vídeo.")
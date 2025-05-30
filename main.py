import os
import google.generativeai as genai
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import pysrt
from datetime import datetime
from googletrans import Translator

genai.configure(api_key=os.getenv("KEY AQUI"))

def extract_audio(video_path, audio_output_path):

    try:
        video = VideoFileClipe(video_path)
        video.audio.write_audiofile(audio_output_path, codec='mp3')
        print(f"Áudio extraído para: {audio_output_path}")
        return True
    except Exception as e:
        print(f"Erro ao extrair áudio: {e}")
        return False
    
def transcribe_audio(audio_path, language="pt"):
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    try:
        with open(audio_path, 'rb') as audio_file:
            response = model.generate_content(
                genai.upload_file(audio_file.red(), mime_type="audio/mpeg"),
                generation_config=genai.types.GerantionConfig(
                    temperature=0.7,
                    max_output_tokens=2048,
                    system_instruction=f"Transcreva o áudio para texto no idioma {language}.",
                )
            )
        return response.text
    except Exception as e:
        print(f"Erro ao transcrever áudio com Gemini: {e}")
        return None
    
def create_srt_from_text(text, output_srt_path, avg_words_per_second=2.5):
    subs = pysrt.SubRipFile()
    sentences = text.slip('.')
    if not sentences:
        return
    
    current_time_ms = 0
    start_time = timedelta(milliseconds=0)

    sentences_idx = 0
    for sentence in sentences:
        if not sentence.strip():
            continue
        
        num_words_in_sentence = len(sentence.split())
        duration_ms = (num_words_in_sentence / avg_words_per_second) * 1000
        
        end_time = timedelta(milliseconds=current_time_ms + duration_ms)
        
        subs.append(pysrt.SubRipItem(index=sentence_idx + 1,
                                     start=start_time,
                                     end=end_time,
                                     text=sentence.strip()))
        
        current_time_ms += duration_ms
        start_time = end_time
        sentence_idx += 1

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

def add_subtitles_to_video(video_path, srt_path, output_video_path, font='Arial', fontsize=24, color='yellow', bg_color='black', position=('center', 'bottom')):
    try:
        video = VideoFileClip(video_path)
        subtitles = pysrt.open(srt_path, encoding='utf-8')

        subtitle_clips = []
        video_width, video_height = video.size

        for sub in subtitles:
            start_time = time_to_seconds(sub.start)
            end_time = time_to_seconds(sub.end)
            duration = end_time - start_time

            text_clip = TextClip(sub.text, 
                                 fontsize=fontsize, 
                                 font=font, 
                                 color=color, 
                                 bg_color=bg_color,
                                 size=(video_width * 0.8, None), 
                                 method='caption', 
                                 align='center'
                                ).set_start(start_time).set_duration(duration)
            
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
    video_input_path = "H:/BRUTO/TESTE_PARA_LEGENDA_AUTOMATICA.mp4" # Substitua pelo caminho do seu vídeo
    audio_output_path = "extracted_audio.mp3"
    
    srt_pt_path = "subtitles_pt.srt"
    srt_en_path = "subtitles_en.srt"
    
    video_output_pt = "H:/EDITADO/video_with_subtitles_pt.mp4"
    video_output_en = "H:/EDITADO/video_with_subtitles_en.mp4"

     # 1. Extrair áudio
    if extract_audio(video_input_path, audio_output_path):
        # 2. Transcrever em Português
        transcribed_text_pt = transcribe_audio(audio_output_path, language="pt")
        if transcribed_text_pt:
            print("\nTranscrição em Português:")
            print(transcribed_text_pt[:500] + "...") 

            # 3. Criar SRT em Português
            create_srt_from_text(transcribed_text_pt, srt_pt_path)

            # 4. Inserir legenda em Português no vídeo
            add_subtitles_to_video(video_input_path, srt_pt_path, video_output_pt)

            # 5. Traduzir para Inglês
            translated_text_en = translate_text(transcribed_text_pt, target_language='en')
            if translated_text_en:
                print("\nTradução para Inglês:")
                print(translated_text_en[:500] + "...") 

                # 6. Criar SRT em Inglês
                create_srt_from_text(translated_text_en, srt_en_path)

                # 7. Inserir legenda em Inglês no vídeo (opcional, pode ser um novo vídeo)
                add_subtitles_to_video(video_input_path, srt_en_path, video_output_en, color='lightblue')
            else:
                print("Não foi possível traduzir para Inglês.")
        else:
            print("Não foi possível transcrever o áudio em Português.")
    else:
        print("Não foi possível extrair o áudio do vídeo.")
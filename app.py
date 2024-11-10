from flask import Flask, render_template, request, send_file, redirect, url_for
import yt_dlp
import os
from moviepy.editor import VideoFileClip


app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def download_youtube_video(link, quality):
    """Télécharger une vidéo YouTube avec la qualité spécifiée en utilisant yt-dlp."""
    try:
        ydl_opts = {
            'format': f'best[height<={quality}]',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'noplaylist': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        print(f"Erreur lors du téléchargement de la vidéo YouTube : {e}")
        return None

def download_youtube_audio(link):
    """Télécharger uniquement l'audio d'une vidéo YouTube en utilisant yt-dlp."""
    try:
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'noplaylist': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        print(f"Erreur lors du téléchargement de l'audio YouTube : {e}")
        return None

def convert_to_audio(video_path, audio_path):
    """Convertir un fichier vidéo en audio (MP3)."""
    try:
        video = VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(audio_path)
        return audio_path
    except Exception as e:
        print(f"Erreur lors de la conversion de la vidéo en audio : {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    choice = request.form.get('choice')
    filepath = None
    message = "Choix invalide"

    if choice == '1':
        link = request.form.get('link')
        quality = request.form.get('quality')
        filepath = download_youtube_video(link, quality)
        message = "Vidéo téléchargée avec succès" if filepath else "Échec du téléchargement de la vidéo."

    elif choice == '2':
        linkaudio = request.form.get('linkaudio')
        filepath = download_youtube_audio(linkaudio)
        message = "Audio téléchargé avec succès" if filepath else "Échec du téléchargement de l'audio."

    elif choice == '3':
        file = request.files.get('file')
        if file and file.filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            pathaudio = convert_to_audio(file_path, f"{file_path}.mp3")
            filepath = pathaudio
            message = "Audio converti avec succès" if filepath else "Échec de la conversion de la vidéo."

    return render_template('result.html', message=message, filepath=filepath)

@app.route('/download/<path:filepath>', methods=['GET'])
def download(filepath):
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

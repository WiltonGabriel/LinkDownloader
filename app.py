from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from yt_dlp import YoutubeDL
import tempfile
import os
import shutil

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    link = data.get('link')
    download_format = data.get('format')

    if not link:
        return jsonify({"error": "Nenhum link fornecido."}), 400

    temp_dir = tempfile.mkdtemp()
    cookie_file_path = None

    try:
        cookies_string = os.environ.get('COOKIES')
        
        if cookies_string:
            with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_cookie_file:
                temp_cookie_file.write(cookies_string)
                cookie_file_path = temp_cookie_file.name

        ydl_opts = {
            'outtmpl': os.path.join(temp_dir, '%(title).20s-%(id)s.%(ext)s'),
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'force_overwrites': True,
            'buffer_size': '256K',
            'cookiefile': cookie_file_path,  # Mantenha apenas esta linha
        }

        if download_format == 'mp4':
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            mimetype = 'video/mp4'
        elif download_format == 'mp3':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
            mimetype = 'audio/mpeg'
        else:
            return jsonify({"error": "Formato de download inválido."}), 400

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            file_path = ydl.prepare_filename(info_dict)
            
            if download_format == 'mp3':
                base, ext = os.path.splitext(file_path)
                file_path = base + '.mp3'

        if not os.path.exists(file_path):
             raise FileNotFoundError("O arquivo baixado não foi encontrado.")

        download_name = os.path.basename(file_path)

        return send_file(
            file_path,
            as_attachment=True,
            download_name=download_name,
            mimetype=mimetype
        )

    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"error": "Ocorreu um erro no download. Verifique o link ou o formato do vídeo."}), 500
    
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        if cookie_file_path and os.path.exists(cookie_file_path):
            os.remove(cookie_file_path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

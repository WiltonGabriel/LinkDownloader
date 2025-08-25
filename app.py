# app.py

from flask import Flask, request, jsonify, render_template, Response, stream_with_context
from flask_cors import CORS
import subprocess
import os
import tempfile

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

    cookie_file_path = None
    temp_cookie_file = None
    try:
        # Gerencia o arquivo de cookies temporário se a variável de ambiente existir
        cookies_string = os.environ.get('COOKIES')
        if cookies_string:
            temp_cookie_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt')
            temp_cookie_file.write(cookies_string)
            cookie_file_path = temp_cookie_file.name
            temp_cookie_file.close()

        # --- Passo 1: Obter o nome do arquivo primeiro (operação rápida) ---
        filename_cmd = ['yt-dlp', '--get-filename', '-o', '%(title).25s-%(id)s.%(ext)s', link]
        if cookie_file_path:
            filename_cmd.extend(['--cookie', cookie_file_path])
        
        # Ajusta o comando para obter a extensão correta (.mp3)
        if download_format == 'mp3':
            filename_cmd.extend(['--extract-audio', '--audio-format', 'mp3'])

        try:
            original_filename = subprocess.check_output(filename_cmd, stderr=subprocess.PIPE).decode('utf-8').strip()
            if download_format == 'mp3':
                base, _ = os.path.splitext(original_filename)
                download_name = f"{base}.mp3"
            else:
                download_name = original_filename
        except subprocess.CalledProcessError as e:
            print(f"Erro ao obter nome do arquivo: {e.stderr.decode('utf-8', errors='ignore')}")
            return jsonify({"error": "Link inválido ou vídeo indisponível."}), 500

        # --- Passo 2: Preparar o comando de download para streaming ---
        if download_format == 'mp4':
            mimetype = 'video/mp4'
            download_cmd = [
                'yt-dlp', link,
                '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                '-o', '-',  # Saída para stdout (para streaming)
            ]
        elif download_format == 'mp3':
            mimetype = 'audio/mpeg'
            download_cmd = [
                'yt-dlp', link,
                '-f', 'bestaudio/best',
                '--extract-audio',
                '--audio-format', 'mp3',
                '--audio-quality', '192K',
                '-o', '-',  # Saída para stdout
            ]
        else:
            return jsonify({"error": "Formato de download inválido."}), 400

        if cookie_file_path:
            download_cmd.extend(['--cookie', cookie_file_path])
        
        # --- Passo 3: Iniciar o processo e fazer o streaming da resposta ---
        process = subprocess.Popen(download_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        def generate_stream():
            try:
                # Lê a saída do processo em pedaços e envia para o cliente
                while True:
                    chunk = process.stdout.read(4096)
                    if not chunk:
                        break
                    yield chunk
                
                # Verifica se houve algum erro durante o processo
                stderr_output = process.stderr.read().decode('utf-8', errors='ignore')
                if process.wait() != 0:
                    print(f"Erro no yt-dlp: {stderr_output}")
            finally:
                # Garante que o processo seja finalizado
                process.terminate()

        headers = {
            'Content-Disposition': f'attachment; filename="{download_name}"',
            'Content-Type': mimetype
        }

        # Usa stream_with_context para transmitir a resposta
        return Response(stream_with_context(generate_stream()), headers=headers)

    except Exception as e:
        print(f"Erro inesperado: {e}")
        return jsonify({"error": "Ocorreu um erro inesperado no servidor."}), 500
    finally:
        # Limpa o arquivo de cookie temporário
        if cookie_file_path and os.path.exists(cookie_file_path):
            os.remove(cookie_file_path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

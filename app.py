# app.py (versão aprimorada)

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
    process = None  # Inicializa a variável do processo

    try:
        cookies_string = os.environ.get('COOKIES')
        if cookies_string:
            temp_cookie_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt')
            temp_cookie_file.write(cookies_string)
            cookie_file_path = temp_cookie_file.name
            temp_cookie_file.close()

        filename_cmd = ['yt-dlp', '--get-filename', '-o', '%(title).25s-%(id)s.%(ext)s', link]
        if cookie_file_path:
            filename_cmd.extend(['--cookie', cookie_file_path])
        if download_format == 'mp3':
            filename_cmd.extend(['--extract-audio', '--audio-format', 'mp3'])

        try:
            original_filename = subprocess.check_output(filename_cmd).decode('utf-8').strip()
            if download_format == 'mp3':
                base, _ = os.path.splitext(original_filename)
                download_name = f"{base}.mp3"
            else:
                download_name = original_filename
        except subprocess.CalledProcessError:
            return jsonify({"error": "Link inválido ou vídeo indisponível."}), 500

        if download_format == 'mp4':
            mimetype = 'video/mp4'
            download_cmd = [
                'yt-dlp', link,
                # Opcional: limite a qualidade para economizar ainda mais recursos
                # '-f', 'best[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best',
                '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                '-o', '-',
            ]
        elif download_format == 'mp3':
            mimetype = 'audio/mpeg'
            download_cmd = [
                'yt-dlp', link,
                '-f', 'bestaudio/best',
                '--extract-audio',
                '--audio-format', 'mp3',
                '--audio-quality', '192K',
                '-o', '-',
            ]
        else:
            return jsonify({"error": "Formato de download inválido."}), 400

        if cookie_file_path:
            download_cmd.extend(['--cookie', cookie_file_path])

        # MELHORIA: Removido 'stderr=subprocess.PIPE' para evitar deadlocks.
        # Erros agora irão para os logs padrão do Render, o que é mais seguro.
        process = subprocess.Popen(download_cmd, stdout=subprocess.PIPE)

        def generate_stream():
            # O bloco try/except/finally garante a finalização do processo
            # mesmo que o usuário cancele o download.
            try:
                while True:
                    chunk = process.stdout.read(4096)
                    if not chunk:
                        break
                    yield chunk
                process.wait() # Espera o processo terminar normalmente
            except GeneratorExit:
                print("Conexão fechada pelo cliente.")
            finally:
                # Lógica de limpeza crucial
                if process.poll() is None:  # Verifica se o processo ainda está rodando
                    print(f"Processo {process.pid} ainda em execução. Finalizando...")
                    process.terminate() # Envia sinal para terminar
                    process.wait() # Espera a finalização
                    print(f"Processo {process.pid} finalizado.")

        headers = {
            'Content-Disposition': f'attachment; filename="{download_name}"',
            'Content-Type': mimetype
        }

        return Response(stream_with_context(generate_stream()), headers=headers)

    except Exception as e:
        print(f"Erro inesperado: {e}")
        return jsonify({"error": "Ocorreu um erro inesperado no servidor."}), 500
    finally:
        if cookie_file_path and os.path.exists(cookie_file_path):
            os.remove(cookie_file_path)
        # Garante que, em caso de erro ANTES do streaming, o processo seja limpo
        if process and process.poll() is None:
            print(f"Finalizando processo {process.pid} no bloco finally principal.")
            process.terminate()
            process.wait()

if __name__ == '__main__':
    app.run(debug=True, port=5000)

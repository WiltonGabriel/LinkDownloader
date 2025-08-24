const inputD = document.getElementById('inputDownload');
const verificarBtn = document.getElementById('verificar-btn');
const downloadArea = document.getElementById('download-area');

const clearBtn = document.getElementById('clear-btn');

verificarBtn.addEventListener('click', () => {
    const link = inputD.value;

    if (link.includes('youtube.com') || link.includes('youtu.be') || link.includes('instagram.com') || link.includes('facebook.com')) {

        if (link.length > 20) {
            downloadArea.style.display = 'block';
            downloadArea.innerHTML = `
                <p>Seu link é válido! Escolha uma opção de download:</p>
                <button id="download-mp4">Baixar MP4</button>
                <button id="download-mp3">Baixar MP3</button>
            `;
            verificarBtn.style.display = 'none';

            clearBtn.style.display = 'block';

            const downloadMP4 = document.getElementById('download-mp4');
            const downloadMP3 = document.getElementById('download-mp3');

            downloadMP4.addEventListener('click', () => {
                downloadArea.innerHTML = '<p>Preparando o download do vídeo...</p>';
                fetch('/download', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ link: link, format: 'mp4' })
                })
                .then(response => {
                    if (response.ok) {
                        const contentDisposition = response.headers.get('Content-Disposition');
                        const filename = contentDisposition ? contentDisposition.split('filename=')[1].replace(/['"]/g, '') : 'video-download.mp4';
                        return response.blob().then(blob => ({ blob, filename }));
                    }
                    throw new Error('Erro no servidor.');
                })
                .then(({ blob, filename }) => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    downloadArea.innerHTML = '<p>Download concluído!</p>';
                })
                .catch(error => {
                    downloadArea.innerHTML = `<p style="color:red;">Erro: ${error.message}</p>`;
                });
            });

            downloadMP3.addEventListener('click', () => {
                downloadArea.innerHTML = '<p>Preparando o download do áudio...</p>';
                fetch('/download', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ link: link, format: 'mp3' })
                })
                .then(response => {
                    if (response.ok) {
                        const contentDisposition = response.headers.get('Content-Disposition');
                        const filename = contentDisposition ? contentDisposition.split('filename=')[1].replace(/['"]/g, '') : 'audio-download.mp3';
                        return response.blob().then(blob => ({ blob, filename }));
                    }
                    throw new Error('Erro no servidor.');
                })
                .then(({ blob, filename }) => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    downloadArea.innerHTML = '<p>Download concluído!</p>';
                })
                .catch(error => {
                    downloadArea.innerHTML = `<p style="color:red;">Erro: ${error.message}</p>`;
                });
            });

        } else {
            downloadArea.style.display = 'block';
            downloadArea.innerHTML = '<p>Por favor, insira um link completo e válido.</p>';
        }

    } else {
        downloadArea.style.display = 'block';
        downloadArea.innerHTML = '<p>Por favor, insira um link do YouTube, Instagram ou Facebook.</p>';
    }
});

clearBtn.addEventListener('click', () => {
    downloadArea.style.display = 'none';
    inputD.value = '';
    verificarBtn.style.display = 'block';
    clearBtn.style.display = 'none';
});

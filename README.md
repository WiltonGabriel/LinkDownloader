# LinkDownloader

## Sobre o Projeto

Este é um projeto simples que criei para resolver um problema pessoal: meu pai vive pedindo para eu baixar vídeos do Facebook e do YouTube para ele postar nos status.

Para facilitar a vida, decidi criar esta ferramenta usando Python e Flask. É um aplicativo web fácil de usar, onde qualquer um pode simplesmente colar o link e baixar o vídeo ou áudio.

## Como Funciona?

* **Frontend:** A página principal é feita com HTML, CSS e JavaScript. É onde você cola o link do vídeo.
* **Backend:** Quando você clica em baixar, o link é enviado para o meu código em Python. Lá, a biblioteca `yt-dlp` faz o trabalho de baixar o vídeo ou áudio para você.

## Tecnologias Utilizadas

* **Python:** A linguagem de programação principal.
* **Flask:** O framework web que usei para criar o servidor.
* **`yt-dlp`:** Uma biblioteca para baixar os vídeos.
* **`gunicorn`:** O servidor que roda o projeto online.

## Como Rodar o Projeto na Sua Máquina

Se você quiser testar o projeto no seu computador, siga estes passos:

1.  **Baixe o código:**

    ```
    git clone [https://github.com/WiltonGabriel/LinkDownloader.git](https://github.com/WiltonGabriel/LinkDownloader.git)
    cd LinkDownloader
    ```

2.  **Instale as dependências:**

    ```
    pip install -r requirements.txt
    ```

3.  **Inicie o servidor:**

    ```
    flask run
    ```

    O site vai abrir no seu navegador.

## Onde o Projeto Está Online?

Você pode acessar a versão hospedada do projeto aqui: <https://linkdownloader-kcoy.onrender.com>

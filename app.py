from flask import Flask,render_template, request, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from selectionar_persona import *
from selecionar_documento import *
from assistente_ecomart import *
import uuid

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4o"

app = Flask(__name__)
app.secret_key = 'alura'

caminho_imagem_enviada = None

assistente = carregar_bot(modelo=modelo)
thread_id = assistente["thread_id"]
assistente_id = assistente["assistant_id"]
file_ids = assistente["file_ids"]

@app.route("/upload_imagem", methods=["POST"])
def upload_imagem():
    global caminho_imagem_enviada
    if 'imagem' in request.files:
        imagem_enviada = request.files['imagem']
        
        nome_arquivo = str(uuid.uuid4()) + os.path.splitext(imagem_enviada.filename)[1]
        caminho_arquivo = os.path.join(UPLOAD_FOLDER, nome_arquivo)
        imagem_enviada.save(caminho_arquivo)
        caminho_imagem_enviada = caminho_arquivo
        print (caminho_imagem_enviada)
        return "Imagem recebida com sucesso!", 200
    return "Nenhuma imagem recebida.", 400
    
@app.route("/chat", methods=["POST"])
def chat():
    global caminho_imagem_enviada
    print (caminho_imagem_enviada)
    prompt = request.json["msg"]
    resultado = enviar_mensagem(assistente_id=assistente_id, thread_id=thread_id, prompt=prompt, caminho_imagem_enviada=caminho_imagem_enviada)
    resposta = resultado.content[0].text.value
    return resposta


@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug = True)

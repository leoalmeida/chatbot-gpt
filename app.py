from flask import Flask,render_template, request, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from selectionar_persona import *
from selecionar_documento import *
from assistente_ecomart import *

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4-1106-preview"

app = Flask(__name__)
app.secret_key = 'alura'

assistente = carregar_bot(modelo=modelo)
thread_id = assistente["thread_id"]
assistente_id = assistente["assistant_id"]
file_ids = assistente["file_ids"]

@app.route("/chat", methods=["POST"])
def chat():
    prompt = request.json["msg"]
    resultado = enviar_mensagem(assistente_id=assistente_id, thread_id=thread_id, prompt=prompt)
    resposta = resultado.content[0].text.value
    return resposta


@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug = True)

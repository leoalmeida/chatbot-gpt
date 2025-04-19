from flask import Flask,render_template, request, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4"

app = Flask(__name__)
app.secret_key = 'alura'

contexto = carrega("documentos/ecomart.txt")

def bot(prompt_usuario):
    maximo_tentativas = 1
    repeticao = 0
    while True:
        try:
            prompt_sistema = f"""
            Você é um chatbot de atendimento a clientes de um e-commerce.
            Você não deve responder perguntas que não sejam dados do ecommerce informado!
            # Contexto
            {contexto}
            """
            resposta = cliente.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": prompt_usuario}
                ],
                temperature=1,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                model = modelo
            )
            return resposta
        except Exception as erro:
            repeticao += 1
            if repeticao >= maximo_tentativas:
                    return "Erro no GPT: %s" % erro
            print('Erro de comunicação com OpenAI:', erro)
            sleep(1)

@app.route("/chat", methods=["POST"])
def chat():
    prompt = request.json["msg"]
    resultado = bot(prompt_usuario=prompt)
    resposta = resultado.choices[0].message.content
    return resposta


@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug = True)

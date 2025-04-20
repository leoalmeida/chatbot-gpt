from openai import OpenAI
from helpers import *
from dotenv import load_dotenv
import os
from selectionar_persona import *
from selecionar_documento import *
from assistente_ecomart import *

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPΕΝΑΙ_API_KEY"))

def bot(prompt_usuario):
    maximo_tentativas = 1
    repeticao = 0
    persona = personas[selecionar_persona(prompt_usuario=prompt_usuario)]
    print('Persona:', persona)
    contexto = selecionar_contexto(prompt_usuario=prompt_usuario)
    documento_selecionado = selecionar_documento(resposta_opeai=contexto)
    while True:
        try:
            prompt_sistema = f"""
            Você é um chatbot de atendimento a clientes de um e-commerce.
            Você não deve responder perguntas que não sejam dados do ecommerce informado!
            Você deve gerar respostas utilizando o contexto abaixo.
            Você deve adotar a persona abaixo.

            # Contexto
            {documento_selecionado}

            # Persona
            {persona}
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
from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4"

politicas_ecomart = carrega('documentos/politicas_ecomart.txt')
dados_ecomart = carrega('documentos/dados_ecomart.txt')
produtos_ecomart = carrega('documentos/produtos_ecomart.txt')
dados_completos = carrega('documentos/ecomart.txt')

def selecionar_documento(resposta_opeai="todos"):
    if "politicas" in resposta_opeai:
        return dados_ecomart + "\n" + politicas_ecomart
    elif "produtos" in resposta_opeai:  
        return dados_ecomart + "\n" + produtos_ecomart
    else: return dados_completos

def selecionar_contexto(prompt_usuario):
    prompt_sistema = f"""
    A empresa EcoMart possui três documentos principais que detalham diferentes aspectos do negócio:

    #Documento 1 "\n {dados_ecomart} "\n"
    #Documento 2 "\n" {politicas_ecomart} "\n"
    #Documento 3 "\n" {produtos_ecomart} "\n"

    Avalie o prompt do usuário e retorne o documento mais indicado para ser usado no contexto da resposta. Retorne dados se for o Documento 1, políticas se for o Documento 2 e produtos se for o Documento 3. 

    """

    resposta = cliente.chat.completions.create(
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": prompt_usuario}
        ],
        temperature=1,
        model = modelo
    )
    contexto = resposta.choices[0].message.content.strip().lower()

    return contexto
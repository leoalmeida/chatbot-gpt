from openai import OpenAI
from helpers import *
from dotenv import load_dotenv
import os
from helpers import encodar_imagem

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPΕΝΑΙ_API_KEY"))
modelo = "gpt-4o"

def analisar_imagem(caminho_de_imagem):
    prompt = f"""
        Assuma que você é um assistente de chatbot e que provaelmente o usuário está enviado a foto de
        um produto. Faça uma análise dele, e se for um produto com defeito, emita um parecer. Assuma que você sabe e
        processou uma imagem com o Vision e a resposta será informada no formato de saída.

        # FORMATO DA RESPOSTA
       
         Minha análise para imagem consiste em: Parecer com indicações do defeito ou descrição do produto (se não houver defeito)

        ## Descreva a imagem
        coloque a descrição aqui
    """
    imagem_base64 = encodar_imagem(caminho_de_imagem)

    resposta = cliente.chat.completions.create(
        model=modelo,
        messages=[
            {
            "role": "user",
            "content": [
                {
                    "type": "text", "text": prompt
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{imagem_base64}",
                },
                },
            ],
            }
        ],
        max_tokens=300
    )
    
    return resposta.choices[0].message.content
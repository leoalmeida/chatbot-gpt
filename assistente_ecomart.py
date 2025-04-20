from openai import OpenAI
from helpers import *
from dotenv import load_dotenv
import os
from selectionar_persona import *
from selecionar_documento import *
from tools_ecomart import *
import json
from vision_ecomart import analisar_imagem

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPΕΝΑΙ_API_KEY"))

STATUS_COMPLETED = "completed" 
STATUS_REQUIRES_ACTION = "requires_action" 

UPLOAD_FOLDER='documentos'

def apagar_assistente(assistant_id):
    cliente.beta.assistants.delete(assistant_id)
    
def apagar_thread(thread_id):
    cliente.beta.threads.delete(thread_id)

def apagar_vector_store(vs_id):
    cliente.vector_stores.delete(vs_id)

def apagar_arquivos(lista_ids_arquivos):
    for id_arquivo in lista_ids_arquivos:
        cliente.files.delete(id_arquivo)

def visualizar_historico(thread_id):
    historico = cliente.beta.threads.messages.list(thread_id=thread_id).data
    return list(historico)

def enviar_mensagem(assistente_id, thread_id, prompt, caminho_imagem_enviada=None):
    maximo_tentativas = 1
    repeticao = 0

    while True:
        try:
            persona = personas[selecionar_persona(prompt)]

            cliente.beta.threads.messages.create(
                thread_id=thread_id,
                role = "user",
                content =  f"""
                Assuma, de agora em diante, a personalidade abaixo. 
                Ignore as personalidades anteriores.

                # Persona
                {persona}
                """
            )

            resposta_vision=""
            if caminho_imagem_enviada != None:
                resposta_vision = analisar_imagem(caminho_imagem_enviada)
                resposta_vision+= ". Na resposta final, apresente detalhes da descrição da imagem."
                os.remove(caminho_imagem_enviada)
                caminho_imagem_enviada = None
            print("Resposta: "+resposta_vision)
            cliente.beta.threads.messages.create(
                thread_id=thread_id, 
                role = "user",
                content = resposta_vision+prompt
            )
            
            run = cliente.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistente_id
            )
            
            while run.status != STATUS_COMPLETED:
                run = cliente.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
                print(f"Status: {run.status}")
                if run.status == STATUS_REQUIRES_ACTION:
                    tools_acionadas = run.required_action.submit_tool_outputs.tool_calls
                    respostas_tools_acionadas = []
                    for uma_tool in tools_acionadas:
                        nome_funcao = uma_tool.function.name
                        funcao_escolhida = minhas_funcoes[nome_funcao]
                        argumentos = json.loads(uma_tool.function.arguments)
                        print(argumentos)
                        resposta_tool = funcao_escolhida(argumentos)
                        respostas_tools_acionadas.append({
                                "tool_call_id": uma_tool.id,
                                "output": resposta_tool
                        })
                    run = cliente.beta.threads.runs.submit_tool_outputs(
                            thread_id = thread_id,
                            run_id = run.id,
                            tool_outputs=respostas_tools_acionadas
                    )


            historico = visualizar_historico(thread_id=thread_id)
            resposta = historico[0]
            return resposta
        except Exception as erro:
            repeticao += 1
            if repeticao >= maximo_tentativas:
                    return "Erro no GPT: %s" % erro
            print('Erro de comunicação com OpenAI:', erro)
            sleep(1)
            
def criar_thread():
    return cliente.beta.threads.create()

def criar_assistente( modelo = "gpt-4"):
    assistente = cliente.beta.assistants.create(
        name="Atendente EcoMart",
        instructions = f"""
            Você é um chatbot de atendimento a clientes de um e-commerce. 
            Você não deve responder perguntas que não sejam dados do ecommerce informado!
            Além disso, acesse os arquivos associados a você e a thread para responder as perguntas.
            """,
        model = modelo,
        tools= minhas_tools,
        tool_resources= minha_tool_resources
    )
    print(assistente.id)
    return assistente

def criar_vector_store(lista_ids_arquivos):
    vector_store = cliente.vector_stores.create(name="vs_assistant", file_ids=lista_ids_arquivos)
    print(vector_store.file_counts)
    minha_tool_resources['file_search']['vector_store_ids'].append(vector_store.id)
    return vector_store.id

def criar_lista_ids():
    lista_ids_arquivos = []

    file_dados = cliente.files.create(
        file=open("documentos/dados_ecomart.txt", "rb"),
        purpose="assistants"
    )
    lista_ids_arquivos.append(file_dados.id)

    file_politicas = cliente.files.create(
        file=open("documentos/politicas_ecomart.txt", "rb"),
        purpose="assistants"
    )
    lista_ids_arquivos.append(file_politicas.id)

    file_produtos = cliente.files.create(
        file=open("documentos/produtos_ecomart.txt","rb"),
        purpose="assistants"
    )

    lista_ids_arquivos.append(file_produtos.id)

    return lista_ids_arquivos

def carregar_bot(modelo):
    filename = "documentos/assistentes.json"
    if not os.path.exists(filename):
        file_id_list = criar_lista_ids()
        vs_id = criar_vector_store(file_id_list)
        assistente = criar_assistente(modelo=modelo)
        thread = criar_thread()
        data = {
            "assistant_id": assistente.id,
            "thread_id": thread.id,
            "vector_store_id": vs_id,
            "file_ids": file_id_list
        }
        try:
            with open(filename, "w", encoding="utf-8") as arquivo:
                json.dump(data, arquivo, ensure_ascii=False, indent=4)
            print("Arquivo 'assistentes.json' criado com sucesso.")
        except IOError as e:
            print(f"Erro ao salvar arquivo: {e}")
    try:
        with open(filename, "r", encoding="utf-8") as arquivo:
            data = json.load(arquivo)
            print("Arquivo 'assistentes.json' carregado com sucesso.")
            return data
    except FileNotFoundError:
        print("Arquivo 'assistentes.json' não encontrado")



     
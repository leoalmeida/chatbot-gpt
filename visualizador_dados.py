from openai import OpenAI

client = OpenAI(api_key="SUA_CHAVE_API")

file = client.files.create(
  file=open("documentos\data.csv", "rb"),
  purpose='assistants'
)
  
assistant = client.beta.assistants.create(
  name="Robô de finanças pessoais",
  description="Um assistente excelente em criar projeções financeiras",
  instructions="Você é um assistente amigável.",
  model="gpt-4-1106-preview",
  tools=[{"type": "code_interpreter"}]
)

thread = client.beta.threads.create(
  messages=[
    {
      "role": "user",
      "content": "Crie 3 visualizações de dados com base nas tendências deste arquivo.",
      "attachments": [
        {
          "type": "file",
          "file_id": file.id
        }
      ]
    }
  ]
)

run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id
)

STATUS_COMPLETED = "completed"
while run.status != STATUS_COMPLETED:
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
    print(run.status)

historico = list(client.beta.threads.messages.list(thread_id=thread.id).data)
resposta = historico[0]
print("Resposta: ", resposta)

client.files.delete(file.id)
client.beta.assistants.delete(assistant_id=assistant.id)
client.beta.threads.delete(thread_id=thread.id)

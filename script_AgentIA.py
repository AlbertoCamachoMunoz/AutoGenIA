import tempfile
import json
import requests
import mwparserfromhell

from autogen.agentchat import AssistantAgent, UserProxyAgent, register_function
from autogen.coding import LocalCommandLineCodeExecutor

# Configuración del modelo
config_list = [
    {
        "model": "llama-3.2-1b-instruct",
        "base_url": "http://localhost:1234/v1",  # lite-llm
        "api_key": "token",
    }
]

# Definición de funciones disponibles
function_list = [
    {
        "name": "wikipedia_search",
        "description": "Perform a search on Wikipedia",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Name of the article to search for",
                }
            },
            "required": ["title"],
        },
    }
]

# Prompt del sistema
SYSTEM_PROMPT = """
You are a knowledgeable librarian that answers questions from your supervisor.
For research tasks, only use the functions provided to you. Check the functions output and make your answer.
Constraints:
- Think step by step.
- Be accurate and precise.
- Answer briefly, in few words.
- Reflect on your answer, and if you think you are hallucinating, reformulate the answer.
- When you receive the result of a tool call, use it to respond to the supervisor, and then add the word "TERMINATE"
- Do not repeat yourself
"""

# Mensaje inicial del sistema
system_message = {"role": "system", "content": SYSTEM_PROMPT}

# Configuración del entorno de ejecución de código
temp_dir = tempfile.TemporaryDirectory()
code_executor_config = LocalCommandLineCodeExecutor(
    timeout=30,
    work_dir=temp_dir.name,
)

# Definición del agente asistente
agent = AssistantAgent(
    name="librarian",
    system_message=SYSTEM_PROMPT,
    human_input_mode="NEVER",
    llm_config={
        "functions": function_list,
        "config_list": config_list,
        "timeout": 280,
        "temperature": 0.2,
    },
)

# Definición del agente usuario
user = UserProxyAgent(
    name="supervisor",
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=1,
    code_execution_config={"excutor": code_executor_config, "use_docker": False},
)

# Implementación de la función herramienta
def wikipedia_search(title: str) -> str:
    response = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "revisions",
            "rvprop": "content",
        },
    ).json()

    page = next(iter(response["query"]["pages"].values()))
    print("página", page)
    wikicode = page["revisions"][0]["*"]
    parsed_wikicode = mwparserfromhell.parse(wikicode)
    content = parsed_wikicode.strip_code()

    print("contenido", content)

    return json.dumps({
        "name": "wikipedia_search",
        "content": content
    })

# Registro de la función en el ecosistema de agentes
register_function(
    wikipedia_search,
    caller=agent,
    executor=user,
    name="wikipedia_search",
    description="Perform a search on Wikipedia",
)

# Inicio del chat
chat_result = user.initiate_chat(
    agent,
    message="Get the content of the Wikipedia page for 'BattleTech'. Then, summarize the page content.",
)

# Resultado del proceso
print(chat_result)
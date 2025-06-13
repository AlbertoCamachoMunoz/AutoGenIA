from autogen.agentchat import AssistantAgent
from application.interfaces.llm_interface import LLMInterface


class PlannerAgentFactory:
    """
    Fábrica para crear un agente planificador (planner) usando AutoGen y un proveedor LLM.
    """

    @staticmethod
    def create(llm_provider: LLMInterface, functions: list = None) -> AssistantAgent:
        """
        Crea un planner de AutoGen con un LLM configurado desde tu proveedor (Gemini, LLM Studio, etc),
        y opcionalmente una lista de funciones que el planner puede invocar.

        Args:
            llm_provider (LLMInterface): Proveedor de LLM inyectado
            functions (list): Lista de funciones que se habilitan para el planner

        Returns:
            AssistantAgent: Agente configurado como planner
        """
        if functions is None:
            functions = []

        llm_config = {
            "config_list": [{
                "model": llm_provider.get_model_name(),
                "base_url": llm_provider.get_base_url(),
                "api_key": llm_provider.get_api_key(),
                "price": [0.0, 0.0]  # Sin coste real si es local
            }],
            "temperature": 0.1,
            "timeout": 30,
            "functions": functions
        }

        return AssistantAgent(
            name="planner",
            system_message=(
                # ●──────── INSTRUCCIONES DEL PLANNER ────────●
                "You are a task-oriented planner.\n"
                "\n"
                "Available tools:\n"
                "  • wikipedia_search(title: str)\n"
                "  • send_email(to: str, subject: str, body: str)\n"
                "\n"
                "Workflow you MUST follow:\n"
                "  1. Call wikipedia_search **exactly once** with {'title': <topic>}.\n"
                "  2. From the user's request, read the desired language code (e.g. \"EN\" in "
                "     {\"lang\":\"EN\", ...}). Translate the Wikipedia text to **that language**.\n"
                "  3. Build the JSON string exactly like {\"lang\":\"<code>\",\"content\":<translation>}.\n"
                "  4. Call send_email with:\n"
                "        to      → e-mail given by the user,\n"
                "        subject → a concise subject in the target language,\n"
                "        body    → the JSON from step 3.\n"
                "  5. After send_email returns SUCCESS, reply only **TERMINATE**.\n"
                "\n"
                "Rules:\n"
                "  • Do NOT call wikipedia_search more than once.\n"
                "  • Do NOT call send_email without every required parameter.\n"
                "  • Never answer the user yourself; rely on tool calls until step 5."
            ),
            llm_config=llm_config,
            max_consecutive_auto_reply=4,          # un poco más de margen
            is_termination_msg=lambda x: "TERMINATE" in x.get("content", "").upper(),
        )
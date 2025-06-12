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
            "temperature": 0.3,
            "timeout": 30,
            "functions": functions
        }

        return AssistantAgent(
            name="planner",
            system_message=(
                "Realiza las tareas que te indique el usuario, si es necesario, espera la respuesta de la wikipedia "
                "y realiza lo que el usuario te indique. Eres un agente planificador. Tu tarea es dividir instrucciones "
                "del usuario en subtareas, y decidir qué agentes deben ejecutarlas. Habla poco, y actúa delegando trabajo. "
                "Puedes invocar funciones de otros agentes si es necesario. Si no puedes resolver la tarea, responde con 'TERMINATE'. "
                "No repitas instrucciones, y no respondas más de 2 veces seguidas."
            ),
            llm_config=llm_config,
            max_consecutive_auto_reply=2,  # Máximo 2 respuestas seguidas
            is_termination_msg=lambda x: "TERMINATE" in x.get("content", "").upper()
        )
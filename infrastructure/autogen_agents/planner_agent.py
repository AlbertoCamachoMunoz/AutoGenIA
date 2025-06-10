# infrastructure/autogen_agents/planner_agent.py

from autogen.agentchat import AssistantAgent
from application.interfaces.llm_interface import LLMInterface


def create_planner_agent(llm_provider: LLMInterface) -> AssistantAgent:
    """
    Crea un planner de AutoGen con un LLM configurado desde tu proveedor (Gemini, LLM Studio, etc).

    Args:
        llm_provider (LLMInterface): Proveedor de LLM inyectado

    Returns:
        AssistantAgent: Agente configurado como planner
    """

    llm_config = {
        "config_list": [{
            "model": llm_provider.get_model_name(),
            "base_url": llm_provider.get_base_url(),
            "api_key": llm_provider.get_api_key(),
        }],
        "temperature": 0.3,
        "timeout": 30
    }

    return AssistantAgent(
        name="planner",
        system_message=(
            "Eres un agente planificador. Tu tarea es dividir instrucciones del usuario en subtareas, "
            "y decidir qué agentes deben ejecutarlas. Habla poco, y actúa delegando trabajo."
        ),
        llm_config=llm_config
    )

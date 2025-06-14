# infrastructure/autogen_agents/planner_agent.py

from typing import Any
from autogen.agentchat import AssistantAgent
from application.interfaces.llm_interface import LLMInterface
from infrastructure.autogen_agents.mappers.planner_mapper import PlannerMapper
from application.dtos.planner_app_response import PlannerAppResponse


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
            system_message="""
You are a task-oriented planner.
Available tools:
  • wikipedia_search(title: str)
  • send_email(to: str, subject: str, body: str)

Workflow you MUST follow:
  1. Call wikipedia_search **exactly once** with {'title': <topic>}.
  2. From the user's request, read the desired language code (e.g. "EN" in {"lang":"EN", ...}). Translate the Wikipedia text to **that language**.
  3. Build the JSON string exactly like {"lang":"<code>","content":<translation>}.
  4. Call send_email with:
        to      → e-mail given by the user,
        subject → a concise subject in the target language,
        body    → the JSON from step 3.
  5. After send_email returns SUCCESS, reply only **TERMINATE**.

Rules:
  • Do NOT call wikipedia_search more than once.
  • Do NOT call send_email without every required parameter.
  • Never answer the user yourself; rely on tool calls until step 5.
""",
            llm_config=llm_config,
            max_consecutive_auto_reply=4,
            is_termination_msg=lambda x: "TERMINATE" in x.get("content", "").upper(),
        )

    @staticmethod
    def wrap_planner_output(result: Any) -> PlannerAppResponse:
        """
        Garantiza que cualquier salida del planner sea un PlannerAppResponse válido.
        Evita que devuelva tipos primitivos como int o str directamente.
        """
        return PlannerMapper.map_response(result)
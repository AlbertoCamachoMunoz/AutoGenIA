# infrastructure/autogen_adapters/agent_autogen_wrapper.py
"""
Wrapper genérico que permite a AutoGen invocar cualquiera de los agentes de
infraestructura (Wikipedia, Email, etc.) mediante el mecanismo *function calling*.

✔  Usa el contrato unificado: AgentAppRequest(content=dict)
✔  Elimina la conversión específica por nombre; el agente recibe siempre un
   diccionario con los argumentos originales de la llamada.
"""

import json
import logging
from autogen.agentchat import AssistantAgent

from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse
from application.interfaces.agent_interface import AgentInterface
from infrastructure.autogen_adapters.dtos.function_execution_response_dto import (
    FunctionExecutionResponseDTO,
    FunctionExecutionStatus,
)
from infrastructure.autogen_adapters.mappers.function_execution_mapper import (
    FunctionExecutionMapper,
)

logger = logging.getLogger(__name__)

class AgentAutoGenWrapper(AssistantAgent):
    def __init__(self, name: str, agent_class: type, agent: AgentInterface):
        super().__init__(
            name=name,
            llm_config=False,
            system_message=f"Wrapper del agente «{name}».",
            human_input_mode="NEVER",
        )
        self._agent_class = agent_class
        self._agent = agent

    # --------------------------------------------------------------------- #
    # API pública
    # --------------------------------------------------------------------- #

    def get_agent(self) -> AgentInterface:
        return self._agent

    def get_function_list(self) -> list:
        """Devuelve la lista de funciones que expone el agente real."""
        return self._agent_class.get_function_list()

    def run(self, request: AgentAppRequest) -> AgentAppResponse:
        """Delegates the call to the underlying concrete agent."""
        return self._agent.run(request)

    def execute_function(self, function_call, **kwargs):
        """
        Recibe la llamada propuesta por el planner, la transforma en
        AgentAppRequest y devuelve la respuesta adaptada a AutoGen,
        INCLUYENDO un mensaje válido para el chat del flujo.
        """
        try:
            logger.debug("[%s] execute_function → %s", self.name, function_call)

            # ---------------------------------------------------------- #
            # 1) Normalizar la llamada
            # ---------------------------------------------------------- #
            if isinstance(function_call, str):
                function_call = json.loads(function_call)

            arguments = function_call.get("arguments", {})
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except Exception:
                    # Si es dict serializado en str por el LLM, prueba eval seguro
                    import ast
                    arguments = ast.literal_eval(arguments)

            # ---------------------------------------------------------- #
            # 2) Construir el DTO genérico
            # ---------------------------------------------------------- #
            app_request = AgentAppRequest(content=arguments)
            logger.debug("[%s] app_request → %s", self.name, app_request)

            # ---------------------------------------------------------- #
            # 3) Ejecutar agente real
            # ---------------------------------------------------------- #
            app_response = self._agent.run(app_request)
            logger.debug("[%s] app_response ← %s", self.name, app_response)

            # ---------------------------------------------------------- #
            # 4) Adaptar la salida para AutoGen (mensaje válido)
            # ---------------------------------------------------------- #
            # ¡ESTO es lo que espera el GroupChat! El planner recibirá este mensaje
            return True, {
                "role": self.name,
                "content": app_response.content or "",
                "status": app_response.status.name,
                "message": app_response.message
            }

        except Exception as exc:
            logger.exception("[%s] Error en execute_function", self.name)
            return True, {
                "role": self.name,
                "content": f"ERROR: {str(exc)}",
                "status": "ERROR",
                "message": str(exc)
            }

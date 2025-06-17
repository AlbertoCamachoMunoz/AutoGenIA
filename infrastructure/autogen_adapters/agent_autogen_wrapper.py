# infrastructure/autogen_adapters/agent_autogen_wrapper.py

import json
import logging
from autogen.agentchat import AssistantAgent

from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse
from application.interfaces.agent_interface import AgentInterface
from application.enums.status_code import StatusCode
from infrastructure.autogen_adapters.mappers.function_execution_mapper import FunctionExecutionMapper

logger = logging.getLogger(__name__)


class AgentAutoGenWrapper(AssistantAgent):
    def __init__(self, name: str, agent_class: type, agent: AgentInterface):
        super().__init__(
            name=name,
            llm_config=agent.get_llm_config(),
            system_message= agent.get_llm_prompt() if agent.get_llm_prompt() is not None else f"Wrapper del agente «{name}».",
            human_input_mode="NEVER",
        )
        self._agent_class = agent_class
        self._agent = agent

    def get_agent(self) -> AgentInterface:
        return self._agent

    def get_function_list(self) -> list:
        return self._agent_class.get_function_list()

    def run(self, request: AgentAppRequest) -> AgentAppResponse:
        return self._agent.run(request)

    def execute_function(self, function_call, **kwargs):
        """
        Recibe la llamada propuesta por el planner, la transforma en
        AgentAppRequest y devuelve la respuesta adaptada a AutoGen,
        INCLUYENDO un mensaje válido para el chat del flujo.
        """
        try:
            logger.debug("[%s] execute_function → %s", self.name, function_call)

            if isinstance(function_call, str):
                function_call = json.loads(function_call)

            arguments = function_call.get("arguments", {})
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except Exception:
                    import ast
                    arguments = ast.literal_eval(arguments)

            app_request = AgentAppRequest(content=arguments)
            logger.debug("[%s] app_request → %s", self.name, app_request)

            app_response = self._agent.run(app_request)
            logger.debug("[%s] app_response ← %s", self.name, app_response)

            # ÚNICO CAMBIO: Usar solo el mapper, no crear el dict manualmente
            dto = FunctionExecutionMapper.map_response(self.name, app_response)
            return True, dto.__dict__

        except Exception as exc:
            logger.exception("[%s] Error en execute_function", self.name)
 
            app_response = AgentAppResponse(
                content=f"ERROR: {str(exc)}",
                status=StatusCode.ERROR,
                message=str(exc),
            )
            dto = FunctionExecutionMapper.map_response(self.name, app_response)
            return True, dto.__dict__

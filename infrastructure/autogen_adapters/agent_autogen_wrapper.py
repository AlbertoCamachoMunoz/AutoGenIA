# infrastructure/autogen_adapters/agent_autogen_wrapper.py

import json
from venv import logger
from autogen.agentchat import AssistantAgent
from application.interfaces.agent_interface import AgentInterface
from application.dtos.agent_app_request import AgentAppRequest
from infrastructure.autogen_adapters.dtos.function_execution_request_dto import FunctionExecutionRequestDTO
from infrastructure.autogen_adapters.dtos.function_execution_response_dto import FunctionExecutionResponseDTO, FunctionExecutionStatus
from infrastructure.autogen_adapters.mappers.function_execution_mapper import FunctionExecutionMapper


class AgentAutoGenWrapper(AssistantAgent):

    def __init__(self, name: str, agent_class: type, agent: AgentInterface):

        super().__init__(
            name=name,
            llm_config=False,
            system_message=f"Wrapper del agente «{name}».",
            human_input_mode="NEVER"
        )
        self._agent_class = agent_class
        self._agent = agent

    def get_agent(self):
        return self._agent
    
    def get_function_list(self):
        """Obtiene la lista de funciones soportadas por este agente."""
        return self._agent_class.get_function_list()

    def execute_function(self, function_call, **kwargs):
        try:
            logger.debug(f"[{self.name}] Ejecutando execute_function con: {function_call}")

            if isinstance(function_call, str):
                function_call = json.loads(function_call)
                logger.debug(f"[{self.name}] function_call parseado desde string: {function_call}")

            name = function_call.get("name", self.name)
            arguments = function_call.get("arguments", {})

            if isinstance(arguments, str):
                arguments = json.loads(arguments)
                logger.debug(f"[{self.name}] arguments parseados desde string: {arguments}")

            request_dto = FunctionExecutionRequestDTO(name=name, arguments=arguments)
            logger.debug(f"[{self.name}] request_dto creado: {request_dto}")

            app_request = FunctionExecutionMapper.map_request(request_dto)
            logger.debug(f"[{self.name}] app_request mapeado: {app_request}")

            app_response = self._agent.run(app_request)
            logger.debug(f"[{self.name}] app_response recibido: {app_response}")

            response_dto = FunctionExecutionMapper.map_response(agent_name=self.name, app_response=app_response)
            logger.debug(f"[{self.name}] response_dto generado: {response_dto}")

            return True, response_dto.__dict__

        except Exception as e:
            logger.error(f"[{self.name}] Error en execute_function: {str(e)}", exc_info=True)
            error_dto = FunctionExecutionResponseDTO(
                name=self.name,
                content=str(e),
                status=FunctionExecutionStatus.ERROR
            )
            return True, error_dto.__dict__
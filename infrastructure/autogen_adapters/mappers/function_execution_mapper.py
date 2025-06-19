from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse
from application.enums.status_code import StatusCode
from infrastructure.autogen_adapters.dtos.function_execution_request_dto import FunctionExecutionRequestDTO
from infrastructure.autogen_adapters.dtos.function_execution_response_dto import FunctionExecutionResponseDTO


class FunctionExecutionMapper:
    @staticmethod
    def map_request(dto: FunctionExecutionRequestDTO) -> AgentAppRequest:
        # Toda la llamada va en content
        return AgentAppRequest(content=dto.arguments)

    @staticmethod
    def map_response(agent_name: str, app_response: AgentAppResponse) -> FunctionExecutionResponseDTO:
        # DEVOLVER EL OBJETO DIRECTAMENTE, NUNCA UN STRING (IMPORTANTE PARA ENCADENADO DE FUNCIONES)
        # Mantener la estructura como dict puro, no como string
        # Así el planner puede acceder a 'products', 'status', 'message', etc.

        return FunctionExecutionResponseDTO(
            name=agent_name,
            content={
                "content": app_response.content,
                "status": app_response.status.name,
                "message": app_response.message,
            },
            status=app_response.status
        )

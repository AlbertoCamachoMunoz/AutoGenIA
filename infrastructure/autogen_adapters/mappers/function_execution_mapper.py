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
        return FunctionExecutionResponseDTO(
            name=agent_name,
            content=f"{app_response.content}\n\n[Status: {app_response.status.name}]",
            status=app_response.status
        )
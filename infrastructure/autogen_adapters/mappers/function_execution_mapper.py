from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse
from application.enums.status_code import StatusCode
from infrastructure.autogen_adapters.dtos.function_execution_request_dto import FunctionExecutionRequestDTO
from infrastructure.autogen_adapters.dtos.function_execution_response_dto import FunctionExecutionResponseDTO, FunctionExecutionStatus


class FunctionExecutionMapper:
    @staticmethod
    def map_request(dto: FunctionExecutionRequestDTO) -> AgentAppRequest:
        input_data = dto.arguments.get("title") or dto.arguments.get("query")
        if not input_data:
            raise ValueError(f"Falta 'title' o 'query' en los argumentos de {dto.name}")
        return AgentAppRequest(input_data=input_data)

    @staticmethod
    def map_response(agent_name: str, app_response: AgentAppResponse) -> FunctionExecutionResponseDTO:
        return FunctionExecutionResponseDTO(
            name=agent_name,
            content=f"{app_response.content}\n\n[Status: {app_response.status.name}]",
            status=FunctionExecutionStatus.SUCCESS if app_response.status == StatusCode.SUCCESS else FunctionExecutionStatus.ERROR
        )
from infrastructure.agents.email.dtos.email_request_dto import EmailRequestDTO
from infrastructure.agents.email.dtos.email_response_dto import EmailResponseDTO
from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse
from application.enums.status_code import StatusCode

class EmailMapper:
    @staticmethod
    def map_request(app_request: AgentAppRequest) -> EmailRequestDTO:
        data = app_request.content                  # dict con to/subject/body
        return EmailRequestDTO(
            to      = data["to"],
            subject = data["subject"],
            body    = data["body"]
        )

    @staticmethod
    def map_response(dto: EmailResponseDTO) -> AgentAppResponse:
        return AgentAppResponse(
            content=f"{dto.message} TERMINATE",
            status=dto.status,
            message=dto.message
        )
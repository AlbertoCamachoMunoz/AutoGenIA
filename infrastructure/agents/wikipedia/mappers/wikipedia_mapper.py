# infrastructure/agents/wikipedia/mappers/wikipedia_mapper.py

from infrastructure.agents.wikipedia.dtos.wikipedia_request_dto import WikipediaRequestDTO
from infrastructure.agents.wikipedia.dtos.wikipedia_response_dto import WikipediaResponseDTO
from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse

class WikipediaMapper:
    @staticmethod
    def map_request(app_request: AgentAppRequest) -> WikipediaRequestDTO:
        return WikipediaRequestDTO(title=app_request.input_data)

    @staticmethod
    def map_response(dto: WikipediaResponseDTO) -> AgentAppResponse:
        return AgentAppResponse(
            content=dto.content,
            status=dto.status,
            message=dto.message
        )
# infrastructure/agents/price_analyzer/mappers/price_analyzer_mapper.py

from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse
from application.enums.status_code import StatusCode

from infrastructure.agents.price_analyzer.dtos.price_analyzer_request_dto import PriceAnalyzerRequestDTO
from infrastructure.agents.price_analyzer.dtos.price_analyzer_response_dto import PriceAnalyzerResponseDTO


class PriceAnalyzerMapper:
    @staticmethod
    def map_request(app_request: AgentAppRequest) -> PriceAnalyzerRequestDTO:
        data = app_request.content

        if isinstance(data, dict) and "pages" in data:
            return PriceAnalyzerRequestDTO(pages=data["pages"])

        raise ValueError("El parámetro 'pages' es obligatorio y debe ser un array")

    @staticmethod
    def map_response(dto: PriceAnalyzerResponseDTO) -> AgentAppResponse:
        termination_flag = " TERMINATE" if dto.status == StatusCode.SUCCESS else ""
        resumen_corto = " ".join(dto.summary.split()[:20]) + "..." if len(dto.summary.split()) > 20 else dto.summary

        return AgentAppResponse(
            content=f"{resumen_corto}{termination_flag}",
            status=dto.status,
            message=dto.message,
        )

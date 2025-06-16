# infrastructure/agents/webscraper/mappers/webscraper_mapper.py
import json
from infrastructure.agents.webscraper.dtos.webscraper_request_dto import (
    WebScraperRequestDTO, WebScraperEntryDTO
)
from infrastructure.agents.webscraper.dtos.webscraper_response_dto import (
    WebScraperResponseDTO
)
from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse
from application.enums.status_code import StatusCode


class WebScraperMapper:
    # --------------------- REQUEST ---------------------
    @staticmethod
    def map_request(app_request: AgentAppRequest) -> WebScraperRequestDTO:
        data = app_request.content

        # A) raíz -> pages[]
        if isinstance(data, dict) and "pages" in data:
            return WebScraperRequestDTO(
                entries=[WebScraperEntryDTO(**e) for e in data["pages"]]
            )

        # B) raíz -> url
        if isinstance(data, dict) and "url" in data:
            return WebScraperRequestDTO(
                entries=[WebScraperEntryDTO(url=data["url"],
                                            selector=data.get("selector", ""))]
            )

        # C) string
        if isinstance(data, str):
            return WebScraperRequestDTO(entries=[WebScraperEntryDTO(url=data)])

        # D) AutoGen kwargs
        if isinstance(data, dict) and "kwargs" in data:
            inner = data["kwargs"]
            if isinstance(inner, dict) and "pages" in inner:
                return WebScraperRequestDTO(
                    entries=[WebScraperEntryDTO(**e) for e in inner["pages"]]
                )
            if isinstance(inner, dict) and "url" in inner:
                return WebScraperRequestDTO(
                    entries=[WebScraperEntryDTO(url=inner["url"],
                                                selector=inner.get("selector", ""))]
                )
            if isinstance(inner, str):
                return WebScraperRequestDTO(entries=[WebScraperEntryDTO(url=inner)])

        raise ValueError("Se necesita 'pages' o 'url' en la llamada a web_scrape.")

    # --------------------- RESPONSE --------------------
    @staticmethod
    def map_response(dto: WebScraperResponseDTO) -> AgentAppResponse:
        """
        – Éxito  -> dto.content **ya es** la lista JSON completa.
        – Error  -> devuelve detalle en content.
        """
        if dto.status == StatusCode.SUCCESS:
            # Entregamos la lista JSON tal cual, sin envolverla otra vez.
            return AgentAppResponse(
                content=dto.content,
                status=StatusCode.SUCCESS,
                message="OK",
            )

        return AgentAppResponse(
            content=f"ERROR: {dto.message}",
            status=StatusCode.ERROR,
            message=dto.message,
        )

# infrastructure/agents/webscraper/mappers/webscraper_mapper.py
from infrastructure.agents.webscraper.dtos.webscraper_request_dto import WebScraperRequestDTO, ShopRequestEntry
from infrastructure.agents.webscraper.dtos.webscraper_response_dto import WebScraperResponseDTO, ProductResult
from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse

import json

class WebScraperMapper:
    @staticmethod
    def map_request(request: AgentAppRequest) -> WebScraperRequestDTO:
        data = request.content
        entries = []
        limit_results = data.get("limit_results", False)  # ← Recogemos el flag

        if "shops" in data:
            for shop in data["shops"]:
                entries.append(ShopRequestEntry(
                    url=shop["url"],
                    selector_price=shop["selector_price"],
                    selector_description=shop.get("selector_description", ""),
                    selector_sku=shop.get("selector_sku", {})
                ))
        else:
            entries.append(ShopRequestEntry(
                url=data.get("url", ""),
                selector_price=data.get("selector_price", ""),
                selector_description=data.get("selector_description", ""),
                selector_sku=data.get("selector_sku", {})
            ))
        return WebScraperRequestDTO(entries=entries, limit_results=limit_results)

    @staticmethod
    def map_response(dto: WebScraperResponseDTO) -> AgentAppResponse:
        return AgentAppResponse(
            content=json.dumps([product.__dict__ for product in dto.products], ensure_ascii=False),
            status=dto.status,
            message=dto.message
        )

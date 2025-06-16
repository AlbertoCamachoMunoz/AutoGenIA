# infrastructure/agents/webscraper/mappers/webscraper_mapper.py
from infrastructure.agents.webscraper.dtos.webscraper_request_dto import WebScraperRequestDTO, ShopRequestEntry
from infrastructure.agents.webscraper.dtos.webscraper_response_dto import WebScraperResponseDTO, ProductResult
from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse

import json

class WebScraperMapper:
    @staticmethod
    def map_request(request: AgentAppRequest) -> WebScraperRequestDTO:
        content = request.content
        # Si viene como lista bajo 'shops'
        if 'shops' in content:
            shops = content['shops']
        # Si viene plano, conviértelo en lista de un solo elemento
        elif 'url' in content and 'selector_price' in content:
            shops = [content]
        else:
            shops = []
        entries = []
        for shop in shops:
            entries.append(ShopRequestEntry(
                url=shop.get("url", ""),
                selector_price=shop.get("selector_price", ""),
                selector_description=shop.get("description", ""),
                selector_sku=shop.get("selector_sku", {}),
            ))
        return WebScraperRequestDTO(entries=entries)

    @staticmethod
    def map_response(dto: WebScraperResponseDTO) -> AgentAppResponse:
        return AgentAppResponse(
            content=json.dumps([product.__dict__ for product in dto.products], ensure_ascii=False),
            status=dto.status,
            message=dto.message
        )

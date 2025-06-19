from infrastructure.agents.webscraper.dtos.webscraper_request_dto import WebScraperRequestDTO, ShopRequestEntry
from infrastructure.agents.webscraper.dtos.webscraper_response_dto import WebScraperResponseDTO, ProductResult
from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse
import json

class WebScraperMapper:
    @staticmethod
    def map_request(request: AgentAppRequest) -> WebScraperRequestDTO:
        data = request.content
        limit_results = True  # o ajusta a tu necesidad

        # Si los datos llegan como string JSON, decodifica primero
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except Exception:
                raise ValueError("Error decodificando los argumentos: string inválido")

        # 1. Prioridad máxima: 'shops' a nivel raíz
        if isinstance(data, dict) and "shops" in data:
            shops = data["shops"]
            entries = [
                ShopRequestEntry(
                    url=shop["url"],
                    selector_price=shop["selector_price"],
                    selector_description=shop.get("selector_description", ""),
                    selector_sku=shop.get("selector_sku", {})
                ) for shop in shops
            ]
            return WebScraperRequestDTO(entries=entries, limit_results=limit_results)

        # 2. Siguiente prioridad: 'kwargs' a nivel raíz
        if isinstance(data, dict) and "kwargs" in data and isinstance(data["kwargs"], dict):
            inner = data["kwargs"]
            # a) Si hay 'shops' dentro de kwargs
            if "shops" in inner:
                shops = inner["shops"]
                entries = [
                    ShopRequestEntry(
                        url=shop["url"],
                        selector_price=shop["selector_price"],
                        selector_description=shop.get("selector_description", ""),
                        selector_sku=shop.get("selector_sku", {})
                    ) for shop in shops
                ]
                return WebScraperRequestDTO(entries=entries, limit_results=limit_results)
            # b) Si hay parámetros sueltos dentro de kwargs
            entries = [
                ShopRequestEntry(
                    url=inner.get("url", ""),
                    selector_price=inner.get("selector_price", ""),
                    selector_description=inner.get("selector_description", ""),
                    selector_sku=inner.get("selector_sku", {})
                )
            ]
            return WebScraperRequestDTO(entries=entries, limit_results=limit_results)

        # 3. Úl

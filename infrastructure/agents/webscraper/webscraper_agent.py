# infrastructure/agents/webscraper/webscraper_agent.py

import requests
from bs4 import BeautifulSoup

from application.enums.status_code import StatusCode
from application.interfaces.agent_interface import AgentInterface
from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse

from buffer.shared_buffer import get_last_json, set_last_json
from infrastructure.agents.webscraper.dtos.webscraper_request_dto import WebScraperRequestDTO
from infrastructure.agents.webscraper.dtos.webscraper_response_dto import WebScraperResponseDTO, ProductResult
from infrastructure.agents.webscraper.mappers.webscraper_mapper import WebScraperMapper

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

class WebScraperAgent(AgentInterface):
    @staticmethod
    def get_function_name() -> str:
        return "web_scrape"

    @staticmethod
    def get_function_description() -> str:
        return (
            "Scrapea múltiples productos de una o varias URLs (precio, descripción y SKU por producto, selectores configurables)."
        )

    @staticmethod
    def get_function_list() -> list:
        return [
            {
                "name": WebScraperAgent.get_function_name(),
                "description": WebScraperAgent.get_function_description(),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "shops": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "url": {"type": "string"},
                                    "selector_price": {"type": "string"},
                                    "selector_description": {"type": "string"},
                                    "selector_sku": {
                                        "type": "object",
                                        "properties": {
                                            "tag": {"type": "string"},
                                            "attribute": {"type": "string"}
                                        },
                                        "required": ["tag", "attribute"]
                                    }
                                },
                                "required": ["url", "selector_price", "selector_description", "selector_sku"]
                            }
                        }
                    },
                    "required": ["shops"],
                    "additionalProperties": False,
                },
            }
        ]
    
    def run(self, request: AgentAppRequest) -> AgentAppResponse:
        print("WebScraperAgent - request.content:", request.content)
        try:
            req: WebScraperRequestDTO = WebScraperMapper.map_request(request)
            print("WebScraperAgent - req.entries:", req.entries)
            products = []

            for entry in req.entries:
                print("Procesando entry:", entry)
                r = requests.get(entry.url, headers=HEADERS, timeout=15)
                r.raise_for_status()
                soup = BeautifulSoup(r.text, "html.parser")
                print("HTML descargado OK, buscando productos...")

                for prod in soup.find_all(entry.selector_sku["tag"], attrs={entry.selector_sku["attribute"]: True}):
                    sku = prod.get(entry.selector_sku["attribute"], "")

                    meta_wrapper = prod.find_parent(class_="meta-wrapper")
                    if not meta_wrapper:
                        print(f"SKU: {sku} sin meta-wrapper, saltando")
                        continue

                    price_elem = meta_wrapper.select_one(entry.selector_price)
                    desc_elem = meta_wrapper.select_one(entry.selector_description)

                    price = price_elem.get_text(strip=True) if price_elem else ""
                    description = desc_elem.get_text(strip=True) if desc_elem else ""

                    print(f"→ description: {description} | price: {price} | sku: {sku}")

                    products.append(ProductResult(description=description, price=price, sku=sku))

                    if req.limit_results and len(products) > 3:
                        print("[INFO] Límite de productos alcanzado")
                        break

            print("Productos extraídos:", products)

            # --- DEVOLUCIÓN HOMOGENEIZADA PARA FLUJO AUTOGEN ---
            content = {
                "products": [p.__dict__ for p in products],  # Asegúrate que ProductResult es serializable (usa __dict__ o dataclass.asdict)
            }
            dto = WebScraperResponseDTO(
                products=products,
                status=StatusCode.SUCCESS,
                message="OK"
            )

            set_last_json(dto.to_dict())
            print("\n WebScraperAgent   ------  get_last_json:", get_last_json())

            return AgentAppResponse(
                content=content,
                status=StatusCode.SUCCESS,
                message="OK"
            )

        except Exception as exc:
            print("EXCEPCIÓN en WebScraperAgent:", exc)
            print("\n WebScraperAgent con excepcion   ------  get_last_json:", get_last_json())
            set_last_json(dto.to_dict())
            return AgentAppResponse(
                content={"products": []},
                status=StatusCode.ERROR,
                message=str(exc)
            )

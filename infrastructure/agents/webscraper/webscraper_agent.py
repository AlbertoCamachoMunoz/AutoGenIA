from typing import Optional, Dict, Any
import requests
from bs4 import BeautifulSoup

from application.enums.status_code import StatusCode
from application.interfaces.agent_interface import AgentInterface
from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse
from application.interfaces.llm_interface import LLMInterface

from infrastructure.agents.webscraper.dtos.webscraper_request_dto import WebScraperRequestDTO
from infrastructure.agents.webscraper.dtos.webscraper_response_dto import WebScraperResponseDTO, ProductResult
from infrastructure.agents.webscraper.mappers.webscraper_mapper import WebScraperMapper
from infrastructure.autogen_agents.shared_buffer import get_last_json, set_last_json

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

class WebScraperAgent(AgentInterface):
    def __init__(self, provider: Optional[LLMInterface] = None):
        self.provider = provider

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

    def get_llm_config(self) -> Optional[Dict[str, Any]]:
        print("URL Agente scrapper en el get_llm_config:", self.provider.get_base_url_for_agent())
        return {
            "config_list": [{
                "model": self.provider.get_model_name(),
                "base_url": "http://localhost:1234/v1",  # Ajusta según corresponda
                "api_key": self.provider.get_api_key(),
            }],
            "temperature": 0.0,
            "timeout": 360,
        }
    
    def get_llm_prompt(self) -> str:
        return (
            "You are a data extraction agent specialized in e-commerce product pages.\n"
            "- Your task is to scrape product information from a given web page using the provided CSS selectors.\n"
            "- For each product found, extract the description, price, and SKU using the specified selectors.\n"
            "- Return only the raw extracted data, without any commentary, summaries, or formatting.\n"
            "- Do not infer or generate content; if a value cannot be found, leave it empty.\n"
            "- Output must be strictly the result of the extraction, not a generated or rephrased text.\n"
            "- Do not attempt to translate, summarize, or interpret product data—only extract and return as found on the page.\n"
        )

    def execute_function(self, request: AgentAppRequest) -> AgentAppResponse:
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

            set_last_json(content)
            print("\n WebScraperAgent   ------  get_last_json:", get_last_json())

            return AgentAppResponse(
                content=content,
                status=StatusCode.SUCCESS,
                message="OK"
            )

        except Exception as exc:
            print("EXCEPCIÓN en WebScraperAgent:", exc)
            print("\n WebScraperAgent con excepcion   ------  get_last_json:", get_last_json())
            return AgentAppResponse(
                content={"products": []},
                status=StatusCode.ERROR,
                message=str(exc)
            )

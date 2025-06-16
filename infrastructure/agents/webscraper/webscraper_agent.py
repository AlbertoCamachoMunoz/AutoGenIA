# infrastructure/agents/webscraper/webscraper_agent.py
import json
import requests
from bs4 import BeautifulSoup

from application.interfaces.agent_interface import AgentInterface
from application.enums.status_code import StatusCode
from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse

from infrastructure.agents.webscraper.dtos.webscraper_request_dto import (
    WebScraperRequestDTO,
)
from infrastructure.agents.webscraper.dtos.webscraper_response_dto import (
    WebScraperResponseDTO,
)
from infrastructure.agents.webscraper.mappers.webscraper_mapper import (
    WebScraperMapper,
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}


class WebScraperAgent(AgentInterface):
    # ──────────── Metadatos ────────────
    @classmethod
    def get_function_name(cls) -> str:
        return "web_scrape"

    @classmethod
    def get_function_description(cls) -> str:
        return "Scrapea texto visible de una o varias URL (CSS selector opcional)."

    @classmethod
    def get_function_list(cls) -> list:
        """
        Devuelve el schema JSON de la función expuesta a AutoGen.
        Dos formatos aceptados mediante `oneOf`.
        """
        return [
            {
                "name": cls.get_function_name(),
                "description": cls.get_function_description(),
                "parameters": {
                    "type": "object",
                    "oneOf": [
                        {   # A · Una sola página
                            "required": ["url"],
                            "properties": {
                                "url":      {"type": "string"},
                                "selector": {"type": "string"},
                            },
                        },
                        {   # B · Varias páginas
                            "required": ["pages"],
                            "properties": {
                                "pages": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "required": ["url"],
                                        "properties": {
                                            "url":      {"type": "string"},
                                            "selector": {"type": "string"},
                                        },
                                    },
                                }
                            },
                        },
                    ],
                },
            }
        ]

    # ──────────── Ejecución ────────────
    def run(self, request: AgentAppRequest) -> AgentAppResponse:
        try:
            req: WebScraperRequestDTO = WebScraperMapper.map_request(request)
            bloques: list[dict] = []

            for e in req.entries:
                try:
                    print(f"[Scraper] ⇒ {e.url} (selector: {e.selector or '-'})")
                    txt = self._scrape(e.url, e.selector)
                    bloques.append({"url": e.url, "status": "SUCCESS", "content": txt.strip()})
                except Exception as page_exc:
                    bloques.append({"url": e.url, "status": "ERROR", "content": str(page_exc)})

            dto = WebScraperResponseDTO(
                content=json.dumps(bloques, ensure_ascii=False),
                status=StatusCode.SUCCESS,
                message="OK",
            )
            return WebScraperMapper.map_response(dto)

        except Exception as exc:
            dto = WebScraperResponseDTO(
                content="",
                status=StatusCode.ERROR,
                message=str(exc),
            )
            return WebScraperMapper.map_response(dto)

    # ──────────── Helper ────────────
    def _scrape(self, url: str, selector: str = "") -> str:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        if selector:
            nodes = soup.select(selector)
            if not nodes:
                raise ValueError(f"Selector '{selector}' vacío en {url}")
            return "\n".join(n.get_text(" ", strip=True) for n in nodes)

        return soup.get_text(" ", strip=True)

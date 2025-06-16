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


# Cabeceras para imitar un navegador moderno
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}


class WebScraperAgent(AgentInterface):
    # ────────────────────────── Metadatos ──────────────────────────
    @classmethod
    def get_function_name(cls) -> str:
        return "web_scrape"

    @classmethod
    def get_function_description(cls) -> str:
        return (
            "Obtiene el texto visible de una o varias páginas web, "
            "utilizando selectores CSS opcionales."
        )

    @classmethod
    def get_function_list(cls) -> list:
        return [
            {
                "name": cls.get_function_name(),
                "description": cls.get_function_description(),
                "parameters": {
                    "type": "object",
                    "oneOf": [
                        {  # A · Una página
                            "required": ["url"],
                            "properties": {
                                "url":      {"type": "string"},
                                "selector": {"type": "string"},
                            },
                        },
                        {  # B · Lote
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

    # ────────────────────────── Ejecución ──────────────────────────
    def run(self, request: AgentAppRequest) -> AgentAppResponse:
        try:
            req: WebScraperRequestDTO = WebScraperMapper.map_request(request)
            resultados: list[dict] = []

            for entry in req.entries:
                print(f"[Scraper] ⇒ {entry.url} (selector: {entry.selector or '-'})")
                try:
                    texto = self._scrape(entry.url, entry.selector)
                    resultados.append({
                        "url": entry.url,
                        "status": "SUCCESS",
                        "content": texto.strip()
                    })
                except Exception as page_exc:
                    resultados.append({
                        "url": entry.url,
                        "status": "ERROR",
                        "content": str(page_exc)
                    })

            dto = WebScraperResponseDTO(
                content=json.dumps(resultados, ensure_ascii=False),
                status=StatusCode.SUCCESS,
                message="OK"
            )
            return WebScraperMapper.map_response(dto)

        except Exception as exc:
            dto = WebScraperResponseDTO(
                content="",
                status=StatusCode.ERROR,
                message=str(exc)
            )
            return WebScraperMapper.map_response(dto)

    # ───────────────────── Helper privado ──────────────────────
    def _scrape(self, url: str, selector: str = "") -> str:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        if selector:
            nodos = soup.select(selector)
            if not nodos:
                raise ValueError(f"Selector '{selector}' vacío en {url}")
            return "\n".join(n.get_text(" ", strip=True) for n in nodos)

        return soup.get_text(" ", strip=True)

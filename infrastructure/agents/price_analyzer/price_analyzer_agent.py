# infrastructure/agents/price_analyzer/price_analyzer_agent.py

from application.interfaces.agent_interface import AgentInterface
from application.enums.status_code import StatusCode
from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse
from infrastructure.agents.price_analyzer.mappers.price_analyzer_mapper import PriceAnalyzerMapper
from infrastructure.agents.price_analyzer.dtos.price_analyzer_response_dto import PriceAnalyzerResponseDTO
from infrastructure.agents.price_analyzer.dtos.price_analyzer_request_dto import PriceAnalyzerRequestDTO

import re


class PriceAnalyzerAgent(AgentInterface):
    @classmethod
    def get_function_name(cls) -> str:
        return "price_analyze"

    @classmethod
    def get_function_description(cls) -> str:
        return "Analiza los precios obtenidos desde múltiples webs."

    @classmethod
    def get_function_list(cls) -> list:
        return [{
            "name": cls.get_function_name(),
            "description": cls.get_function_description(),
            "parameters": {
                "type": "object",
                "properties": {
                    "pages": {
                        "type": "array",
                        "description": "Listado de páginas con el contenido scrapeado",
                        "items": {
                            "type": "object",
                            "properties": {
                                "url": {"type": "string"},
                                "content": {"type": "string"}
                            },
                            "required": ["url", "content"]
                        }
                    }
                },
                "required": ["pages"]
            }
        }]

    def run(self, request: AgentAppRequest) -> AgentAppResponse:
        try:
            dto: PriceAnalyzerRequestDTO = PriceAnalyzerMapper.map_request(request)

            prices = []
            for page in dto.pages:
                extracted = self._extract_prices(page["content"])
                prices.extend([(page["url"], p) for p in extracted])

            if not prices:
                return PriceAnalyzerMapper.map_response(
                    PriceAnalyzerResponseDTO(summary="No se encontraron precios.", status=StatusCode.ERROR)
                )

            values = [p for _, p in prices]
            resumen = (
                f"Se han detectado {len(values)} precios en total.\n"
                f"• Precio mínimo: {min(values):.2f} €\n"
                f"• Precio máximo: {max(values):.2f} €\n"
                f"• Precio medio:  {sum(values)/len(values):.2f} €\n\n"
                "Detalles por tienda:\n"
            )
            for url, precio in prices:
                resumen += f"→ {url} → {precio:.2f} €\n"

            return PriceAnalyzerMapper.map_response(
                PriceAnalyzerResponseDTO(summary=resumen.strip(), status=StatusCode.SUCCESS)
            )

        except Exception as e:
            return AgentAppResponse(
                content="",
                status=StatusCode.ERROR,
                message=str(e)
            )

    def _extract_prices(self, text: str) -> list[float]:
        matches = re.findall(r"(\d+,\d{2})", text)
        return [float(p.replace(",", ".")) for p in matches]

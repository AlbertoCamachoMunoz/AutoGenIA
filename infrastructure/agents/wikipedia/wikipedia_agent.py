# infrastructure/agents/wikipedia/wikipedia_agent.py

import requests
import mwparserfromhell

from application.interfaces.agent_interface import AgentInterface
from application.enums.status_code import StatusCode  # Importamos el Enum
from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse
from infrastructure.agents.wikipedia.mappers.wikipedia_mapper import WikipediaMapper
from infrastructure.agents.wikipedia.dtos.wikipedia_request_dto import WikipediaRequestDTO
from infrastructure.agents.wikipedia.dtos.wikipedia_response_dto import WikipediaResponseDTO

class WikipediaAgent(AgentInterface):
    def run(self, request: AgentAppRequest) -> AgentAppResponse:
        print(f"Agente wikipedia recibe datos para buscar: {request}")
        try:
            internal_request = WikipediaMapper.map_request(request)
            response = self._search(internal_request)
            return WikipediaMapper.map_response(response)
        except Exception as e:
            return AgentAppResponse(
                content="",
                status=StatusCode.ERROR,
                message=str(e)
            )

    def _search(self, request: WikipediaRequestDTO) -> WikipediaResponseDTO:
        try:
            response = requests.get(
                url="https://en.wikipedia.org/w/api.php", 
                params={
                    "action": "query",
                    "format": "json",
                    "titles": request.title,
                    "prop": "revisions",
                    "rvprop": "content"
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            print(f"Agente wikipedia recibe data de su API : {data}")
            page = next(iter(data["query"]["pages"].values()))

            if "revisions" not in page or not page["revisions"]:
                return WikipediaResponseDTO.empty()._replace(
                    status=StatusCode.ERROR,
                    message=f"No se encontró contenido para '{request.title}'"
                )

            wikitext = page["revisions"][0].get("*") or \
                       page["revisions"][0].get("slots", {}).get("main", {}).get("*")

            if not wikitext:
                return WikipediaResponseDTO.empty()._replace(
                    status=StatusCode.ERROR,
                    message=f"Artículo sin contenido: '{request.title}'"
                )

            parsed = mwparserfromhell.parse(wikitext)
            clean_text = parsed.strip_code().strip()

            return WikipediaResponseDTO(
                content=clean_text,
                status=StatusCode.SUCCESS,
                message="Artículo encontrado",
                title=request.title
            )

        except Exception as e:
            return WikipediaResponseDTO.empty()._replace(
                status=StatusCode.ERROR,
                message=str(e)
            )
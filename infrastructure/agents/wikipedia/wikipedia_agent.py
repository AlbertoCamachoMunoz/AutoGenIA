# infrastructure/agents/wikipedia/wikipedia_agent.py

import requests
import mwparserfromhell

from application.interfaces.agent_interface import AgentInterface
from application.enums.status_code import StatusCode
from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse
from infrastructure.agents.wikipedia.dtos.wikipedia_request_dto import WikipediaRequestDTO
from infrastructure.agents.wikipedia.dtos.wikipedia_response_dto import WikipediaResponseDTO
from infrastructure.agents.wikipedia.mappers.wikipedia_mapper import WikipediaMapper


MAX_REDIRECT_DEPTH = 3

class WikipediaAgent(AgentInterface):
    @classmethod
    def get_function_name(cls) -> str:
        return "wikipedia_search"

    @classmethod
    def get_function_description(cls) -> str:
        return "Busca contenido limpio de Wikipedia."

    @classmethod
    def get_function_list(cls) -> list:
        return [
            {
                "name": "wikipedia_search",
                "description": "Busca contenido limpio de Wikipedia.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Título del artículo de Wikipedia"}
                    },
                    "required": ["title"],
                    # "additionalProperties": False          # ⬅️ esto impide 'search', 'kwargs', etc.
                }
            }
        ]

    def get_llm_config(self) -> None:
        return None
    
    def get_llm_prompt(self) -> None:
        return None
    
    def run(self, request: AgentAppRequest) -> AgentAppResponse:
        print(f"Agente wikipedia recibe datos para buscar: {request}")
        try:
            internal_request = WikipediaMapper.map_request(request)
            response = self._search(internal_request, depth=0)
            return WikipediaMapper.map_response(response)
        except Exception as e:
            return AgentAppResponse(
                content="",
                status=StatusCode.ERROR,
                message=str(e)
            )

    def _search(self, request: WikipediaRequestDTO, depth: int = 0) -> WikipediaResponseDTO:
        if depth > MAX_REDIRECT_DEPTH:
            return WikipediaResponseDTO(
                content="",
                status=StatusCode.ERROR,
                message=f"Profundidad máxima de redirección alcanzada ({MAX_REDIRECT_DEPTH})"
            )

        try:
            response = requests.get(
                url="https://en.wikipedia.org/w/api.php", 
                params={
                    "action": "query",
                    "format": "json",
                    "titles": request.title,
                    "prop": "revisions",
                    "rvprop": "content",
                    "rvslots": "main"
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            page = next(iter(data["query"]["pages"].values()))

            if "revisions" not in page or not page["revisions"]:
                raise ValueError(f"No se encontró contenido para '{request.title}'")

            wikitext = page["revisions"][0].get("slots", {}).get("main", {}).get("*") \
                     or page["revisions"][0].get("*")

            if not wikitext:
                raise ValueError(f"Artículo vacío o sin contenido: '{request.title}'")

            parsed = mwparserfromhell.parse(wikitext)
            clean_text = parsed.strip_code().strip()

            if "#REDIRECT" in wikitext.upper():
                target_title = parsed.filter_wikilinks()[0].title.strip_code().strip()
                print(f"[INFO] Redirigiendo desde '{request.title}' a '{target_title}'")
                return self._search(WikipediaRequestDTO(title=target_title), depth + 1)

            return WikipediaResponseDTO(
                content=clean_text,
                status=StatusCode.SUCCESS,
                message="Artículo encontrado",
                title=request.title
            )

        except requests.RequestException as e:
            return WikipediaResponseDTO(
                content="",
                status=StatusCode.ERROR,
                message=f"Error en la llamada a Wikipedia: {str(e)}"
            )

        except (StopIteration, KeyError, IndexError) as e:
            return WikipediaResponseDTO(
                content="",
                status=StatusCode.ERROR,
                message=f"Formato de respuesta no válido de Wikipedia"
            )

        except Exception as e:
            return WikipediaResponseDTO(
                content="",
                status=StatusCode.ERROR,
                message=f"Error inesperado: {str(e)}"
            )
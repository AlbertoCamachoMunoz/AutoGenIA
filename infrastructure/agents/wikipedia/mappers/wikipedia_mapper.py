# infrastructure/agents/wikipedia/mappers/wikipedia_mapper.py
from infrastructure.agents.wikipedia.dtos.wikipedia_request_dto import (
    WikipediaRequestDTO,
)
from infrastructure.agents.wikipedia.dtos.wikipedia_response_dto import (
    WikipediaResponseDTO,
)
from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse
from application.enums.status_code import StatusCode


class WikipediaMapper:
    @staticmethod
    def map_request(app_request: AgentAppRequest) -> WikipediaRequestDTO:
        """
        Acepta cualquiera de los siguientes formatos en app_request.content
        ───────────────────────────────────────────────────────────────────
        1) {"title": "Italia"}
        2) {"query": "Italia"}                 ← alias admitido
        3) {"kwargs": "Italia"}                ← cuando function_executor usa **kwargs
        4) {"kwargs": {"title": "Italia"}}
        5) {"kwargs": {"query": "Italia"}}
        6) "Italia"                            ← string directo
        """
        data = app_request.content

        # Caso 6: llega un string
        if isinstance(data, str):
            return WikipediaRequestDTO(title=data)

        # Casos 1-2
        if "title" in data:
            return WikipediaRequestDTO(title=data["title"])
        if "query" in data:                     # alias
            return WikipediaRequestDTO(title=data["query"])

        # Casos 3-5
        if "kwargs" in data:
            inner = data["kwargs"]
            if isinstance(inner, str):          # {"kwargs": "Italia"}
                return WikipediaRequestDTO(title=inner)
            if isinstance(inner, dict):
                if "title" in inner:
                    return WikipediaRequestDTO(title=inner["title"])
                if "query" in inner:
                    return WikipediaRequestDTO(title=inner["query"])

        raise ValueError("No se encontró el parámetro 'title' (o 'query') en la llamada")

    @staticmethod
    def map_response(dto: WikipediaResponseDTO) -> AgentAppResponse:
        # Cortamos a 20 palabras
        words = dto.content.split()
        truncated = " ".join(words[:20]) + ("..." if len(words) > 20 else "")

        # Añadimos TERMINATE sólo en éxito
        termination_flag = " TERMINATE" if dto.status == StatusCode.SUCCESS else ""

        return AgentAppResponse(
            content=f"{truncated}{termination_flag}",
            status=dto.status,
            message=dto.message,
        )

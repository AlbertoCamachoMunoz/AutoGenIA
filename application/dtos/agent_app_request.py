# Después
from typing import Any, Dict, Union

from application.enums.status_code import StatusCode

class AgentAppRequest:
    """
    Contenedor genérico enviado a los agentes.
    - content: str | dict  → los datos que el agente necesita.
    """
    def __init__(self, content: Union[str, Dict[str, Any]], status: StatusCode = StatusCode.SUCCESS, message: str = "OK"):
        self.content = content
        self.status = status
        self.message = message
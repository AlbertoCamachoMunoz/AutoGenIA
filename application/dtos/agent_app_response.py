from dataclasses import dataclass
from application.enums.status_code import StatusCode


@dataclass
class AgentAppResponse:
    content: str
    status: StatusCode
    message: str = "OK"
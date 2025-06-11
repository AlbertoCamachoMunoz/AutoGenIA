# application/dtos/agent_app_response.py

from enum import Enum
from dataclasses import dataclass

class StatusCode(Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"

@dataclass
class AgentAppResponse:
    content: str
    status: StatusCode
    message: str = "OK"
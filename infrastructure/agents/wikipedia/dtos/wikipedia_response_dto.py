# infrastructure/agents/wikipedia/dtos/wikipedia_response_dto.py

from enum import Enum
from dataclasses import dataclass

class StatusCode(Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"

@dataclass
class WikipediaResponseDTO:
    content: str
    status: StatusCode
    message: str = "OK"
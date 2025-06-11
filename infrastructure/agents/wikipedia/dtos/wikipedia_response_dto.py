from enum import Enum
from dataclasses import dataclass
from application.enums.status_code import StatusCode

@dataclass
class WikipediaResponseDTO:
    content: str
    status: StatusCode
    message: str = "OK"
    title: str = ""
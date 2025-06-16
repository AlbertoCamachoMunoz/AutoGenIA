# infrastructure/agents/webscraper/dtos/webscraper_response_dto.py

from dataclasses import dataclass
from application.enums.status_code import StatusCode

@dataclass
class WebScraperResponseDTO:
    content: str
    status: StatusCode
    message: str = "OK"

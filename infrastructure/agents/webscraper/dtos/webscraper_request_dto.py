# infrastructure/agents/webscraper/dtos/webscraper_request_dto.py

from dataclasses import dataclass
from typing import Optional, List

@dataclass
class WebScraperEntryDTO:
    url: str
    selector: Optional[str] = ""

@dataclass
class WebScraperRequestDTO:
    entries: List[WebScraperEntryDTO]

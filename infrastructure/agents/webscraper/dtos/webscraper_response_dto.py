# infrastructure/agents/webscraper/dtos/webscraper_response_dto.py
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ProductResult:
    description: str
    price: str
    sku: str

@dataclass
class WebScraperResponseDTO:
    products: List[ProductResult]
    status: str
    message: str
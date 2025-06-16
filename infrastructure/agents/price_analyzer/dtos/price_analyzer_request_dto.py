# infrastructure/agents/price_analyzer/dtos/price_analyzer_request_dto.py

from dataclasses import dataclass

@dataclass
class PriceAnalyzerRequestDTO:
    pages: list  # Lista de diccionarios con campos 'url' y 'content'

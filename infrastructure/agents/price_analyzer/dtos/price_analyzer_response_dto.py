# infrastructure/agents/price_analyzer/dtos/price_analyzer_response_dto.py

from dataclasses import dataclass
from application.enums.status_code import StatusCode

@dataclass
class PriceAnalyzerResponseDTO:
    summary: str
    status: StatusCode
    message: str = "OK"

from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class TranslatedProductSummary:
    url: str
    sku: str
    price: str
    description: str
    translations: Dict[str, str] = field(default_factory=dict)  # Ej: {"EN": "text", "JP": "text"}

@dataclass
class SummaryTranslationResponse:
    products: List[TranslatedProductSummary]
    status: str   # "SUCCESS" | "ERROR"
    message: str = "OK"

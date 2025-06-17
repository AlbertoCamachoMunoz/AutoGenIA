from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ProductTranslated:
    description: str
    price: str
    sku: str
    translations: Dict[str, str]  # p.ej: {'EN': '...', 'PT': '...'}

@dataclass
class TranslatorResponseDTO:
    products: List[ProductTranslated]
    status: str
    message: str

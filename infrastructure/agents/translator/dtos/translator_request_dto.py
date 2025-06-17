from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ProductToTranslate:
    description: str
    price: str
    sku: str

@dataclass
class LangToTranslate:
    lang: str

@dataclass
class TranslatorRequestDTO:
    products: List[ProductToTranslate]
    langs: List[LangToTranslate]

from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class ShopRequestEntry:
    url: str
    selector_price: str
    selector_description: str
    selector_sku: Dict[str, str]  # Ejemplo: {"tag": "a", "attribute": "data-product_sku"}

@dataclass
class WebScraperRequestDTO:
    entries: List[ShopRequestEntry]
    limit_results: bool = False  # ← Nuevo campo

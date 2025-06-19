from dataclasses import dataclass, asdict
from application.enums.status_code import StatusCode

@dataclass
class ProductResult:
    description: str
    price: str
    sku: str

@dataclass
class WebScraperResponseDTO:
    products: list  # List[ProductResult]
    status: StatusCode
    message: str

    def to_dict(self):
        return {
            "products": [asdict(p) for p in self.products],
            "status": self.status.name if isinstance(self.status, StatusCode) else self.status,
            "message": self.message,
        }
from application.dtos.summary_translation_response import SummaryTranslationResponse, TranslatedProductSummary

class SummaryTranslationMapper:
    @staticmethod
    def from_json(raw: list, status: str = "SUCCESS", message: str = "OK") -> SummaryTranslationResponse:
        products = []
        for p in raw:
            translations = {k.replace("description_", "").upper(): v for k, v in p.items() if k.startswith("description_") and k != "description"}
            products.append(
                TranslatedProductSummary(
                    url=p.get("url", ""),   # Asegúrate que el backend añade la URL
                    sku=p.get("sku", ""),
                    price=p.get("price", ""),
                    description=p.get("description", ""),
                    translations=translations
                )
            )
        return SummaryTranslationResponse(products=products, status=status, message=message)

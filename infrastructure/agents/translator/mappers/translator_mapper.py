from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse
from infrastructure.agents.translator.dtos.translator_request_dto import (
    TranslatorRequestDTO, ProductToTranslate, LangToTranslate
)
from infrastructure.agents.translator.dtos.translator_response_dto import (
    TranslatorResponseDTO, ProductTranslated
)

class TranslatorMapper:
    @staticmethod
    def map_request(request: AgentAppRequest) -> TranslatorRequestDTO:
        content = request.content
        # Soporta key "kwargs" igual que en el scrapper
        if isinstance(content, dict) and "kwargs" in content and isinstance(content["kwargs"], dict):
            content = content["kwargs"]

        products = [ProductToTranslate(**prod) for prod in content.get("products", [])]
        langs = [LangToTranslate(**lang) for lang in content.get("langs", [])]
        return TranslatorRequestDTO(products=products, langs=langs)

    @staticmethod
    def map_response(dto: TranslatorResponseDTO) -> AgentAppResponse:
        # Convierte translations dict a campos planos: description_EN, description_PT...
        products_out = []
        for prod in dto.products:
            prod_dict = {
                "description": prod.description,
                "price": prod.price,
                "sku": prod.sku,
            }
            for lang_code, translation in prod.translations.items():
                prod_dict[f"description_{lang_code.upper()}"] = translation
            products_out.append(prod_dict)

        return AgentAppResponse(
            content=products_out,
            status=dto.status,
            message=dto.message
        )

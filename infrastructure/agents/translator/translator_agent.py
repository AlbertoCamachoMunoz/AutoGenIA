from typing import Optional, Dict, Any
from application.interfaces.agent_interface import AgentInterface
from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse
from application.interfaces.llm_interface import LLMInterface
from application.enums.status_code import StatusCode
from infrastructure.agents.translator.dtos.translator_request_dto import TranslatorRequestDTO
from infrastructure.agents.translator.dtos.translator_response_dto import TranslatorResponseDTO, ProductTranslated
from infrastructure.agents.translator.mappers.translator_mapper import TranslatorMapper

LANG_MAP = {
    "english": "EN",
    "en": "EN",
    "portuguese": "PT",
    "pt": "PT",
    "spanish": "ES",
    "es": "ES"
    # Añade más mapeos si quieres
}

class TranslatorAgent(AgentInterface):
    def __init__(self, provider: Optional[LLMInterface] = None):
        self.provider = provider

    @classmethod
    def get_function_name(cls) -> str:
        return "translate_products"

    @classmethod
    def get_function_description(cls) -> str:
        return "Traduce las descripciones de los productos a los idiomas solicitados usando un modelo LLM."

    @classmethod
    def get_function_list(cls) -> list:
        return [
            {
                "name": cls.get_function_name(),
                "description": cls.get_function_description(),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "products": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "description": {"type": "string"},
                                    "price": {"type": "string"},
                                    "sku": {"type": "string"}
                                },
                                "required": ["description", "price", "sku"]
                            }
                        },
                        "langs": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "lang": {"type": "string"}
                                },
                                "required": ["lang"]
                            }
                        }
                    },
                    "required": ["products", "langs"],
                    "additionalProperties": False,
                },
            }
        ]

    def get_llm_config(self) -> Optional[Dict[str, Any]]:
        return {
            "config_list": [{
                "model": self.provider.get_model_name(),
                "base_url": self.provider.get_base_url(),
                "api_key": self.provider.get_api_key(),
            }],
            "temperature": 0.0,
            "timeout": 360,
        }
    
    def get_llm_prompt(self) -> str:
        return (
            "You are a professional translator specialized in product descriptions.\n"
            "- You will receive a product description and a target language.\n"
            "- Return only the translation in the target language, with no extra text, no explanations, and no formatting.\n"
            "- If the description is already in the target language, repeat it exactly as received, with no changes.\n"
            "- Do not modify prices or SKU references, only translate the description text.\n"
            "- Provide accurate and natural translations.\n"
        )

    def run(self, request: AgentAppRequest) -> AgentAppResponse:
        try:
            req: TranslatorRequestDTO = TranslatorMapper.map_request(request)
            translated_products = []

            if not self.provider:
                return TranslatorMapper.map_response(
                    TranslatorResponseDTO(
                        products=[],
                        status=StatusCode.ERROR,
                        message="No LLM provider configured for TranslatorAgent."
                    )
                )

            for prod in req.products:
                translations = {}
                for lang_entry in req.langs:
                    lang_code = LANG_MAP.get(lang_entry.lang.lower(), lang_entry.lang.upper())
                    prompt = (
                        f"Traduce el siguiente texto al idioma '{lang_entry.lang}', responde solo el texto traducido:\n"
                        f"{prod.description}"
                    )
                    response = self.provider.generate(prompt)
                    translations[lang_code] = response.strip() if response else prod.description

                translated_products.append(
                    ProductTranslated(
                        description=prod.description,
                        price=prod.price,
                        sku=prod.sku,
                        translations=translations
                    )
                )

            return TranslatorMapper.map_response(
                TranslatorResponseDTO(
                    products=translated_products,
                    status=StatusCode.SUCCESS,
                    message="OK"
                )
            )

        except Exception as exc:
            return TranslatorMapper.map_response(
                TranslatorResponseDTO(
                    products=[],
                    status=StatusCode.ERROR,
                    message=str(exc)
                )
            )

from typing import Optional, Dict, Any
from application.dtos.llm_app_request import LLMAppRequest
from application.interfaces.agent_interface import AgentInterface
from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse
from application.interfaces.llm_interface import LLMInterface
from application.enums.status_code import StatusCode
from infrastructure.autogen_agents.shared_buffer import set_last_json
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
    # Puedes añadir más mapeos aquí
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
        print("\n=== [TranslatorAgent.run] ===")
        print("Entrada original request.content:")
        print(repr(request.content))
        try:
            req: TranslatorRequestDTO = TranslatorMapper.map_request(request)
            print("→ Después de map_request:")
            print("   products:", req.products)
            print("   langs:", req.langs)

            translated_products = []

            if not self.provider:
                print("✗ No LLM provider configurado.")
                resp = TranslatorMapper.map_response(
                    TranslatorResponseDTO(
                        products=[],
                        status=StatusCode.ERROR,
                        message="No LLM provider configured for TranslatorAgent."
                    )
                )
                print("→ Respuesta generada por error de provider:")
                print("  ", resp)
                return resp

            for idx, prod in enumerate(req.products):
                print(f"\n--- Traduciendo producto {idx+1} ---")
                print("Descripción:", prod.description)
                print("Precio:", prod.price)
                print("SKU:", prod.sku)
                translations = {}
                for lang_idx, lang_entry in enumerate(req.langs):
                    lang_code = LANG_MAP.get(lang_entry.lang.lower(), lang_entry.lang.upper())
                    prompt = (
                        f"Traduce el siguiente texto al idioma '{lang_entry.lang}', responde solo el texto traducido:\n"
                        f"{prod.description}"
                    )
                    print(f"\n   [Producto {idx+1} - Idioma {lang_idx+1}]")
                    print("   Idioma destino:", lang_entry.lang, "| Código:", lang_code)
                    print("   Prompt enviado al LLM:")
                    print(repr(prompt))
                    # Llama al LLM vía provider:
                    llm_app_request = LLMAppRequest(
                        user_input=prompt,
                        status=StatusCode.SUCCESS,
                        message="OK"
                    )
                    response = self.provider.send_data(llm_app_request)
                    print("---------------------------   Respuesta del LLMAppResponse: ---------------------------------")
                    print(response)
                    print(vars(response))
                    print(response.__dict__)
                    print(dir(response))
                    print(response.choices[0].message.content)
                    print("---------------------------   Respuesta del LLMAppResponse: ---------------------------------")
                    print("   Respuesta recibida del LLM (LLMAppResponse):")
                    print("      generated_text:", repr(getattr(response, "generated_text", None)))
                    translations[lang_code] = (
                        response.generated_text.strip() if getattr(response, "generated_text", None) else prod.description
                    )
                    print("   Traducción final almacenada:", translations[lang_code])

                translated_products.append(
                    ProductTranslated(
                        description=prod.description,
                        price=prod.price,
                        sku=prod.sku,
                        translations=translations
                    )
                )
                print("→ Objeto ProductTranslated creado:")
                print("  ", translated_products[-1])

            response_final = TranslatorMapper.map_response(
                TranslatorResponseDTO(
                    products=translated_products,
                    status=StatusCode.SUCCESS,
                    message="OK"
                )
            )
            print("\n→ Respuesta final de TranslatorMapper.map_response:")
            print("  ", response_final)
            print("=== [Fin TranslatorAgent.run] ===\n")
            set_last_json(response_final.content)
            return response_final

        except Exception as exc:
            print("✗ EXCEPCIÓN DETECTADA EN TranslatorAgent.run:", repr(exc))
            response_exc = TranslatorMapper.map_response(
                TranslatorResponseDTO(
                    products=[],
                    status=StatusCode.ERROR,
                    message=str(exc)
                )
            )
            print("→ Respuesta generada por excepción:")
            print("  ", response_exc)
            print("=== [Fin TranslatorAgent.run] ===\n")
            set_last_json(response_exc.content)
            return response_exc

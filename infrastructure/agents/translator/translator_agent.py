from typing import Optional, Dict, Any
from application.dtos.llm_app_request import LLMAppRequest
from application.interfaces.agent_interface import AgentInterface
from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse
from application.interfaces.llm_interface import LLMInterface
from application.enums.status_code import StatusCode
from infrastructure.autogen_agents.shared_buffer import get_last_json, set_last_json
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
        print("URL Agente translator en el get_llm_config:", self.provider.get_base_url_for_agent())
        return {
            "config_list": [{
                "model": self.provider.get_model_name(),
                "base_url": "http://localhost:1234/v1/",  # Ajusta según corresponda
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

    def execute_function(self, request: AgentAppRequest) -> AgentAppResponse:
        print("\n=== [TranslatorAgent.run] ===")
        print("Entrada original request.content:")
        print(repr(request.content))
        try:
            # Cambiado: acepta directamente el dict con "products" y "langs"
            content = request.content if isinstance(request.content, dict) else {}
            products_in = content.get("products", [])
            langs_in = content.get("langs", [])

            print("→ Products recibidos:", products_in)
            print("→ Langs recibidos:", langs_in)

            translated_products = []

            if not self.provider:
                print("✗ No LLM provider configurado.")
                return AgentAppResponse(
                    content={"products": []},
                    status=StatusCode.ERROR,
                    message="No LLM provider configured for TranslatorAgent."
                )

            for idx, prod in enumerate(products_in):
                print(f"\n--- Traduciendo producto {idx+1} ---")
                print("Descripción:", prod.get("description", ""))
                print("Precio:", prod.get("price", ""))
                print("SKU:", prod.get("sku", ""))
                translations = {}
                for lang_idx, lang_entry in enumerate(langs_in):
                    lang_val = lang_entry.get("lang", "")
                    lang_code = LANG_MAP.get(lang_val.lower(), lang_val.upper())
                    prompt = (
                        f"Traduce el siguiente texto al idioma '{lang_val}', responde solo el texto traducido:\n"
                        f"{prod.get('description','')}"
                    )
                    print(f"\n   [Producto {idx+1} - Idioma {lang_idx+1}]")
                    print("   Idioma destino:", lang_val, "| Código:", lang_code)
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
                    print("---------------------------   Respuesta del LLMAppResponse: ---------------------------------")
                    
                    print("   Respuesta recibida del LLM (LLMAppResponse):")
                    print("      generated_text:", repr(getattr(response, "generated_text", None)))
                    translations[lang_code] = (
                        response.generated_text.strip() if getattr(response, "generated_text", None) else prod.get("description", "")
                    )
                    print("   Traducción final almacenada:", translations[lang_code])

                translated_products.append(
                    {
                        "description": prod.get("description", ""),
                        "price": prod.get("price", ""),
                        "sku": prod.get("sku", ""),
                        **{f"description_{code}": value for code, value in translations.items()}
                    }
                )
                print("→ Objeto ProductTranslated creado:")
                print("  ", translated_products[-1])

            # Salida homogeneizada
            response_final = AgentAppResponse(
                content={"products": translated_products},
                status=StatusCode.SUCCESS,
                message="OK"
            )
            set_last_json(response_final.content)
            print("Traductor_Agent   ------  get_last_json:", get_last_json())

            print("\n→ Respuesta final:")
            print("  ", response_final)
            print("=== [Fin TranslatorAgent.run] ===\n")
            return response_final

        except Exception as exc:
            print("✗ EXCEPCIÓN DETECTADA EN TranslatorAgent.run:", repr(exc))
            print("Traductor_Agent con excepcion   ------  get_last_json:", get_last_json())
            return AgentAppResponse(
                content={"products": []},
                status=StatusCode.ERROR,
                message=str(exc)
            )

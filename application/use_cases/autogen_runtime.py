from autogen.agentchat import UserProxyAgent, GroupChat  # type: ignore
from application.mappers.summary_translation_mapper import SummaryTranslationMapper
from application.dtos.summary_translation_response import SummaryTranslationResponse
import json

def run_autogen_chat(user: UserProxyAgent, manager: GroupChat, user_prompt: str) -> SummaryTranslationResponse:
    """
    Lanza la conversación Autogen, extrae el resumen JSON y lo mapea al DTO de dominio.
    """
    chat_result = user.initiate_chat(
        manager,
        message=user_prompt,
        summary_method="reflection_with_llm",
        summary_args={
            "summary_prompt": (
                "Devuelve SOLO el resultado JSON de la traducción (con SKU, precio, descripción original y traducciones),"
                " sin ningún texto extra, sin saludo, sin explicación y sin repetir el prompt del usuario ni mensajes del sistema."
                " Formato: [{sku, price, description, description_<LANG>, ...}]"
            )
        },
        max_turns=6
    )

    try:
        raw_json = chat_result.summary
        print("Raw JSON:", raw_json)  # Debug: mostrar el JSON crudo
        parsed = json.loads(raw_json)
        dto = SummaryTranslationMapper.from_json(parsed)
        return dto
    except Exception as exc:
        return SummaryTranslationMapper.from_json([], status="ERROR", message=f"Error en procesamiento: {exc}")

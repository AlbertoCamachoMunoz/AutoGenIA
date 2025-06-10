from enum import Enum

class LLMProvider(Enum):
    """
    Enum que define los proveedores de modelos de lenguaje (LLM) disponibles.

    Attributes:
        LLM_STUDIO (str): Representa el proveedor LLM Studio ("llm_studio").
        GEMINI (str): Representa el proveedor Gemini ("llm_gemini").
    """
    LLM_STUDIO = "llm_studio"
    GEMINI = "llm_gemini"

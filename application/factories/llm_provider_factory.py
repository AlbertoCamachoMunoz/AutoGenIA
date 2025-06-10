# Archivo: factories/llm_factory.py

from application.interfaces.infrastructure.llm_interface import LLMInterface
from application.enums.llm_provider import LLMProvider

class LLMProviderFactory:
    """
    Factoría para seleccionar el proveedor de LLM.

    Esta clase se encarga de recibir dos instancias que implementan la interfaz LLMInterface
    (por ejemplo, un proveedor para LLM Studio y otro para Gemini) y, en función del tipo de LLM
    solicitado, retorna la instancia correspondiente.

    Uso:
        factory = LLMProviderFactory(llm_studio_instance, gemini_instance)
        llm_provider = factory.get_provider("llm_studio")
    """
    def __init__(self, llm_studio_provider: LLMInterface, gemini_provider: LLMInterface):
        """
        Inicializa la factoría con las instancias de los proveedores de LLM.

        Args:
            llm_studio (LLMInterface): Instancia que implementa el proveedor LLM para LLM Studio.
            llm_gemini (LLMInterface): Instancia que implementa el proveedor LLM para Gemini.
        """
        self.providers = {
            LLMProvider.LLM_STUDIO: llm_studio_provider,
            LLMProvider.GEMINI: gemini_provider
        }
    
    def get_provider(self, llm_type: LLMProvider) -> LLMInterface:
        """
        Retorna la instancia del proveedor de LLM solicitado.

        Este método selecciona la instancia correspondiente al identificador 'llm_type'

        Args:
            llm_type (str): Identificador del proveedor LLM deseado (por ejemplo, "llm_studio" o "llm_gemini").

        Returns:
            LLMInterface: Instancia del proveedor LLM seleccionado.
        """
        # Si no se encuentra el tipo solicitado, se usa "llm_studio" por defecto.
        return self.providers.get(llm_type, self.providers[LLMProvider.LLM_STUDIO])

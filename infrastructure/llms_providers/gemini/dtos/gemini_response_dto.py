from typing import List
from google.genai.types import GenerateContentResponse
import logging

logger = logging.getLogger(__name__)

class GeminiResponseDTO:
    def __init__(self, generated_text: str):
        """
        Inicializa el DTO con el texto generado.

        Args:
            generated_text (str): Texto obtenido del modelo Gemini.
        """
        self.generated_text = generated_text

    @staticmethod
    def from_chunks(chunks: List[GenerateContentResponse]) -> 'GeminiResponseDTO':
        """
        Crea un DTO concatenando texto desde chunks generados por Gemini.

        Args:
            chunks (List[GenerateContentResponse]): Lista de fragmentos generados por Gemini.

        Returns:
            GeminiResponseDTO: DTO con el texto completo generado.

        Raises:
            ValueError: Si algún chunk no tiene el atributo 'text'.
        """
        try:
            generated_text = ''.join(chunk.text for chunk in chunks if hasattr(chunk, 'text'))
            return GeminiResponseDTO(generated_text=generated_text)
        except AttributeError as e:
            logger.error(f"Error al extraer texto de los chunks: {e}")
            raise ValueError("Error al procesar chunks recibidos de Gemini.") from e

    @staticmethod
    def empty() -> 'GeminiResponseDTO':
        """
        Retorna una instancia vacía del DTO, usada principalmente en situaciones de error.

        Returns:
            GeminiResponseDTO: DTO vacío con cadena generada vacía.
        """
        return GeminiResponseDTO(generated_text="")

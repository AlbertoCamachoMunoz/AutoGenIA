from typing import Any, Iterable
from application.dtos.llm_app_request import LLMAppRequest
from application.dtos.llm_app_response import LLMAppResponse
from application.enums.status_code import StatusCode
from infrastructure.llms_providers.gemini.dtos.gemini_request_dto import GeminiRequestDTO
from infrastructure.llms_providers.gemini.dtos.gemini_response_dto import GeminiResponseDTO
from google.genai import types

class GeminiMapper:
    """
    Mapper que convierte solicitudes y respuestas entre los DTOs de la aplicación (LLMAppRequest, LLMAppResponse)
    y los DTOs específicos de Gemini (GeminiRequestDTO, GeminiResponseDTO).

    Esta clase contiene métodos estáticos que facilitan la transformación de datos desde el formato
    utilizado por la aplicación al requerido por la API de Gemini y viceversa.
    """

    @staticmethod
    def map_request(app_request: LLMAppRequest) -> GeminiRequestDTO:
        """
        Convierte un objeto LLMAppRequest en un objeto GeminiRequestDTO para ser utilizado
        al enviar una petición a la API de Google Gemini.

        Args:
            app_request (LLMAppRequest): DTO que representa la solicitud realizada desde la aplicación.
                Contiene la entrada del usuario (user_input) y, opcionalmente, parámetros específicos
                en un diccionario de contexto (context).

        Returns:
            GeminiRequestDTO: DTO formateado específicamente para la API de Gemini, que incluye:
                - model: Modelo a utilizar (por defecto "gemini-2.0-flash" si no se especifica en el contexto).
                - contents: Lista de contenidos que encapsulan la entrada del usuario.
                - config: Configuración de generación que define parámetros como temperatura, top_p, top_k,
                  max_output_tokens y el formato de respuesta.
        """
        # Modelo a usar; valor por defecto: gemini-2.0-flash
        model = app_request.context.get("model", "gemini-2.0-flash")

        # Contenido de la solicitud formateado para Gemini
        contents = [
            types.Content(
                role="user",
                parts=[types.Part(text=app_request.user_input)]
            )
        ]

        # Configuración del proceso de generación de texto
        config = types.GenerateContentConfig(
            temperature=app_request.context.get("temperature", 1),
            top_p=app_request.context.get("top_p", 0.95),
            top_k=app_request.context.get("top_k", 40),
            max_output_tokens=app_request.context.get("max_tokens", 8192),
            response_mime_type="text/plain"
        )

        return GeminiRequestDTO(
            model=model,
            contents=contents,
            config=config
        )

    @staticmethod
    def map_response(dto: GeminiResponseDTO, status_code: int, message: str) -> LLMAppResponse:
        """
        Convierte un objeto GeminiResponseDTO en un objeto LLMAppResponse adecuado para la aplicación.

        Args:
            dto (GeminiResponseDTO): DTO que contiene la respuesta generada por Gemini.
            status_code (int): Código numérico que representa el estado de la respuesta (éxito, error, etc.).
            message (str): Mensaje descriptivo asociado al estado de la respuesta.

        Returns:
            LLMAppResponse: DTO adaptado a la aplicación que encapsula:
                - generated_text: Texto generado por Gemini.
                - status: Estado convertido al Enum StatusCode.
                - message: Mensaje descriptivo del resultado.
        """
        return LLMAppResponse(
            generated_text=dto.generated_text,
            status=StatusCode(status_code),
            message=message
        )

    @staticmethod
    def gemini_response_to_dto(response_chunks: Iterable[Any]) -> GeminiResponseDTO:
        """
        Convierte la respuesta de Gemini recibida como un stream o iterable de objetos
        en un objeto GeminiResponseDTO que encapsula el texto generado.

        Args:
            response_chunks (Iterable[Any]): Iterable de objetos devueltos por Gemini tras la petición.
                Cada elemento (chunk) contiene parte del texto generado.

        Returns:
            GeminiResponseDTO: DTO que contiene el texto completo generado por Gemini,
                obtenido al concatenar el atributo 'text' de cada chunk.
        
        Note:
            Este método puede ampliarse para extraer metadatos adicionales si la API de Gemini los proporciona.
        """
        generated_text = "".join(chunk.text for chunk in response_chunks)

        # Este método podría ampliarse para extraer metadatos adicionales si la API los proporciona.
        return GeminiResponseDTO(generated_text=generated_text)

import logging
import os

from google import genai
from google.api_core.exceptions import (
    GoogleAPIError,
    InvalidArgument,
    ResourceExhausted,
    InternalServerError
)
from google.genai.errors import ClientError

from config.settings import GEMINI_API_KEY
from application.dtos.llm_app_request import LLMAppRequest
from application.dtos.llm_app_response import LLMAppResponse
from application.interfaces.llm_interface import LLMInterface
from application.enums.status_code import StatusCode
from infrastructure.llms_providers.gemini.mappers.gemini_mapper import GeminiMapper
from infrastructure.llms_providers.gemini.dtos.gemini_response_dto import GeminiResponseDTO


class Gemini(LLMInterface):
    """
    Cliente para interactuar con la API de Google Gemini.

    Esta clase se encarga de enviar solicitudes a la API de Gemini utilizando un cliente
    proporcionado por la librería `genai` y de mapear las respuestas a los DTOs definidos
    en la aplicación. Además, implementa un manejo robusto de errores para cubrir distintos
    escenarios de fallo.
    """

    def __init__(self):
        """
        Inicializa la instancia del cliente Gemini con validación de API key.

        Realiza una validación de la API key asegurándose de que esté configurada y cumpla
        con una longitud mínima aproximada. Si la validación falla, se registra un error
        crítico y se lanza una excepción.

        Raises:
            ValueError: Si la API key es inválida o no está configurada.
            Exception: Si ocurre cualquier otro error al inicializar el cliente.
        """
        self.api_key = GEMINI_API_KEY
        self.default_model = "gemini-2.0-flash"
        
        # Validación más estricta de la API key
        if not self.api_key or len(self.api_key) < 30:  # Longitud mínima aproximada
            error_msg = "GEMINI_API_KEY inválida o no configurada en settings.py"
            logging.critical(error_msg)
            raise ValueError(error_msg)

        try:
            self.client = genai.Client(api_key=self.api_key)
            logging.info("Cliente Gemini inicializado correctamente.")
        except Exception as e:
            logging.critical("Error inicializando cliente Gemini: %s", str(e))
            raise

    def send_data(self, app_request: LLMAppRequest) -> LLMAppResponse:
        """
        Envía una petición al servicio Gemini con manejo mejorado de errores.

        Este método transforma la solicitud de la aplicación (LLMAppRequest) al formato
        requerido por la API de Gemini usando el GeminiMapper, y luego envía la solicitud
        mediante el cliente de Gemini. Se implementa un manejo de errores robusto para
        capturar distintos tipos de excepciones y devolver una respuesta consistente.

        Args:
            app_request (LLMAppRequest): DTO que contiene la solicitud realizada por la aplicación.

        Returns:
            LLMAppResponse: Respuesta generada por la API de Gemini encapsulada en un DTO.
                En caso de error, se devuelve un DTO con el estado ERROR y un mensaje descriptivo.
        """
        gemini_request_dto = GeminiMapper.map_request(app_request)

        try:
            logging.info(f"Enviando solicitud a Gemini - Modelo: {gemini_request_dto.model}")
            # Llama a la API de Gemini para generar contenido.
            response_chunks = self.client.models.generate_content_stream(
                model=gemini_request_dto.model,
                contents=gemini_request_dto.contents,
                config=gemini_request_dto.config
            )

            # Convierte el stream de respuesta en un DTO de respuesta.
            gemini_response_dto = GeminiResponseDTO.from_chunks(response_chunks)
            logging.debug("Respuesta recibida correctamente")

            return GeminiMapper.map_response(
                dto=gemini_response_dto,
                status_code=StatusCode.SUCCESS,
                message="OK"
            )
        
        except ClientError as e:
            # Manejo específico para errores de API key
            if "API key not valid" in str(e):
                logging.critical("API KEY INVALIDA: Verifica config/settings.py")
                return self._create_error_response("Error de autenticación: API key inválida o expirada")
            else:
                logging.error("Error de cliente Gemini: %s", str(e))
                return self._create_error_response(f"Error de cliente: {str(e)}")

        except (InvalidArgument, ResourceExhausted, InternalServerError) as e:
            logging.error("Error específico de Gemini (%s): %s", type(e).__name__, str(e))
            return self._create_error_response(f"Error del servicio: {type(e).__name__}")

        except GoogleAPIError as e:
            logging.error("Error general de API: %s", str(e))
            return self._create_error_response(f"Error de comunicación: {str(e)}")

        except Exception as e:
            logging.exception("Error inesperado")
            return self._create_error_response(f"Error interno: {str(e)}")

    def _create_error_response(self, message: str) -> LLMAppResponse:
        """
        Helper para crear respuestas de error consistentes.

        Este método utiliza el GeminiMapper para mapear una respuesta de error, creando
        un DTO vacío de GeminiResponseDTO y asignándole el estado ERROR junto con el mensaje
        proporcionado.

        Args:
            message (str): Mensaje descriptivo del error.

        Returns:
            LLMAppResponse: DTO que representa una respuesta de error.
        """
        return GeminiMapper.map_response(
            dto=GeminiResponseDTO.empty(),
            status_code=StatusCode.ERROR,
            message=message
        )
    
    def get_model_name(self) -> str:
        return self.default_model
    
    def get_base_url(self) -> str:
        # Para compatibilidad, aunque Gemini no usa URL directa
        return "https://generativelanguage.googleapis.com/"
    def get_api_key(self) -> str:
        # Para compatibilidad, aunque Gemini no usa URL directa
        return self.api_key
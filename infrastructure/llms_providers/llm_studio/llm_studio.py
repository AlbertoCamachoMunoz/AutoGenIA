import requests
import logging
from config.settings import LLM_STUDIO_API_URL, LLM_STUDIO_HEADERS, LLM_STUDIO_DEFAULT_NAME, LLM_STUDIO_API_KEY
from application.dtos.llm_app_request import LLMAppRequest
from application.dtos.llm_app_response import LLMAppResponse
from application.interfaces.llm_interface import LLMInterface
from application.enums.status_code import StatusCode  # Importamos el Enum
from infrastructure.llms_providers.llm_studio.dtos.llm_studio_response_dto import LLMStudioResponseDTO
from infrastructure.llms_providers.llm_studio.mappers.llm_studio_mapper import LLMStudioMapper

logger = logging.getLogger(__name__)

class LLMStudio(LLMInterface):
    """
    Implementación de LLMInterface que utiliza el API de LLM Studio.

    Esta clase se encarga de enviar solicitudes al servicio LLM Studio a través de HTTP,
    procesar la respuesta JSON y mapearla a un objeto LLMAppResponse. Se manejan distintos
    escenarios de error para asegurar que se devuelva una respuesta consistente.
    """

    def __init__(self):
        """
        Inicializa la instancia de LLMStudio con la URL y las cabeceras definidas en settings.

        Los parámetros de configuración (API URL y API key) se obtienen del archivo de configuración.
        """
        self.api_url = LLM_STUDIO_API_URL
        self.headers = LLM_STUDIO_HEADERS
        self.default_model = LLM_STUDIO_DEFAULT_NAME
        self.api_key = LLM_STUDIO_API_KEY
        self.base_url = LLM_STUDIO_API_URL

    def send_data(self, app_request: LLMAppRequest) -> LLMAppResponse:
        """
        Envía una solicitud al servicio LLM Studio y devuelve la respuesta mapeada a un LLMAppResponse.

        Este método realiza lo siguiente:
          1. Mapea la solicitud de la aplicación (LLMAppRequest) a un DTO específico para LLM Studio.
          2. Realiza una petición HTTP POST a la API de LLM Studio con un timeout de 10 segundos.
          3. Intenta decodificar la respuesta JSON; si falla, registra el error y retorna una respuesta de error.
          4. Verifica que la respuesta JSON no esté vacía; de lo contrario, retorna un error.
          5. Convierte la respuesta JSON en un DTO interno (LLMStudioResponseDTO) usando el mapper.
          6. Verifica que se hayan recibido opciones válidas; si no, retorna un error.
          7. Mapea el DTO interno a un LLMAppResponse y lo retorna.

        Args:
            app_request (LLMAppRequest): Objeto DTO con la solicitud realizada por la aplicación.

        Returns:
            LLMAppResponse: Objeto que contiene el texto generado, el estado (SUCCESS o ERROR) y un mensaje descriptivo.
        """
        # Mapear la petición de la aplicación al DTO requerido por la infraestructura.
        mapped_request = LLMStudioMapper.map_request(app_request)
        
        try:
            # Realizar la petición HTTP POST con un timeout definido.
            response = requests.post(
                self.api_url,
                json=mapped_request.to_json(),
                headers=self.headers,
                timeout=10  # Timeout de 10 segundos.
            )
            # Si el status code no es 200, se lanza una excepción HTTPError.
            response.raise_for_status()

            # Intentar decodificar la respuesta JSON.
            try:
                response_json = response.json()
            except ValueError as json_error:
                logger.error("Error decodificando JSON: %s", json_error)
                return LLMStudioMapper.map_response(LLMStudioResponseDTO.empty(), StatusCode.ERROR, message="Error decodificando respuesta JSON")
            
            # Comprobar que la respuesta no esté vacía.
            if not response_json:
                logger.error("Respuesta JSON vacía recibida de LLM Studio")
                return LLMStudioMapper.map_response(LLMStudioResponseDTO.empty(), StatusCode.ERROR, message="Respuesta JSON vacía")
            
            dto = LLMStudioMapper.json_to_dto(response_json)
            # Validar que se hayan recibido opciones en la respuesta.
            if not dto.choices:
                logger.warning("La respuesta de LLM Studio no contiene 'choices'")
                return LLMStudioMapper.map_response(LLMStudioResponseDTO.empty(), StatusCode.ERROR, message="Respuesta sin opciones válidas")

            # Mapear el DTO interno a la respuesta de la aplicación.
            return LLMStudioMapper.map_response(dto, StatusCode.SUCCESS, "OK")
        
        except requests.exceptions.HTTPError as http_err:
            logger.error("Error HTTP: %s", http_err)
            return LLMStudioMapper.map_response(LLMStudioResponseDTO.empty(), StatusCode.ERROR, message=f"Error HTTP: {http_err}")
        except requests.exceptions.Timeout as timeout_err:
            logger.error("Tiempo de espera agotado: %s", timeout_err)
            return LLMStudioMapper.map_response(LLMStudioResponseDTO.empty(), StatusCode.ERROR, message="Tiempo de espera agotado")
        except requests.exceptions.RequestException as req_err:
            logger.error("Error en la petición: %s", req_err)
            return LLMStudioMapper.map_response(LLMStudioResponseDTO.empty(), StatusCode.ERROR, message=str(req_err))
        except Exception as e:
            logger.exception("Error inesperado: %s", e)
            return LLMStudioMapper.map_response(LLMStudioResponseDTO.empty(), StatusCode.ERROR, message="Error inesperado")
    
    def get_model_name(self) -> str:
        return self.default_model
    
    def get_base_url(self) -> str:
        # Para compatibilidad, aunque Gemini no usa URL directa
        return self.base_url
    def get_api_key(self) -> str:
        # Para compatibilidad, aunque Gemini no usa URL directa
        return self.api_key

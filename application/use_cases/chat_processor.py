import logging
from application.dtos.data_processing_request import DataProcessingRequest
from application.dtos.llm_app_request import LLMAppRequest
from application.dtos.llm_app_response import LLMAppResponse
from application.dtos.application_response import ApplicationResponse
from application.enums.status_code import StatusCode
from application.interfaces.strategies.data_processing_strategy_interface import DataProcessingStrategyInterface
from application.interfaces.llm_interface import LLMInterface
from application.enums.data_processing_type import DataProcessingType
from application.enums.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

class ChatProcessor:
    """
    Clase que orquesta el flujo completo de interacción con un LLM.
    
    Se divide en tres métodos principales:
      - process_input: Transforma la entrada en una solicitud (LLMAppRequest).
      - send_data: Envía la solicitud al LLM y obtiene una respuesta (LLMAppResponse).
      - process_output: Procesa la respuesta del LLM para obtener el resultado final.
    
    El método process() orquesta la secuencia completa y retorna un ApplicationResponse.
    """

    def __init__(self, llm_provider: LLMInterface, data_processing_strategy: DataProcessingStrategyInterface):
        """
        Inicializa el ChatProcessor con el proveedor de LLM y la estrategia de procesamiento.
        
        Args:
            llm_provider (LLMInterface): Proveedor encargado de enviar datos al LLM.
            data_processing_strategy (DataProcessingStrategyInterface): Estrategia para transformar la entrada y salida.
        """
        self.llm_provider = llm_provider
        self.data_processing_strategy = data_processing_strategy

    def process_input(self, input_data: DataProcessingRequest) -> LLMAppRequest:
        """
        Transforma los datos de entrada en una solicitud para el LLM.
        
        Utiliza la estrategia de procesamiento para convertir la entrada (por ejemplo, texto o audio)
        en un objeto LLMAppRequest que incluye el input, el estado y un mensaje.
        
        Args:
            input_data (DataProcessingRequest): DTO con datos de entrada validados
            
        Returns:
            LLMAppRequest: Solicitud formateada para el LLM.
        """
        logger.info("Procesando entrada...")
        request = self.data_processing_strategy.process_input(input_data)
        logger.debug("Solicitud generada: %s", request.user_input)
        return request

    def send_data(self, llm_request: LLMAppRequest) -> LLMAppResponse:
        """
        Envía la solicitud al proveedor del LLM y obtiene la respuesta.
        
        Se encarga de llamar al método send_data del proveedor y de capturar su respuesta.
        
        Args:
            llm_request (LLMAppRequest): Solicitud generada para el LLM.
            
        Returns:
            LLMAppResponse: Respuesta obtenida del LLM.
        """
        logger.info(f"Enviando datos al LLM... {llm_request.user_input}")
        response = self.llm_provider.send_data(llm_request)
        logger.info(f"Respuesta recibida: {response.generated_text}")
        return response

    def process_output(self, llm_response: LLMAppResponse) -> LLMAppResponse:
        """
        Procesa la respuesta del LLM y la adapta al formato final.
        
        Utiliza la estrategia de procesamiento para transformar la respuesta del LLM en la salida final
        que será presentada a la aplicación.
        
        Args:
            llm_response (LLMAppResponse): Respuesta obtenida del LLM.
            
        Returns:
            LLMAppResponse: Salida final procesada.
        """
        logger.info("Procesando salida del LLM...")
        final_output = self.data_processing_strategy.process_output(llm_response)
        logger.info("Salida final: %s", final_output.generated_text)
        return final_output

    def process(self, data_type: DataProcessingType, llm_type: LLMProvider, input_data: DataProcessingRequest) -> ApplicationResponse:
        """
        Orquesta el flujo completo de interacción con el LLM.
        
        Este método realiza los siguientes pasos:
          1. Llama a process_input para convertir la entrada en un LLMAppRequest.
          1.1. Si la solicitud tiene estado ERROR, retorna un ApplicationResponse de error.
          2. Llama a send_data para enviar la solicitud y obtener la respuesta.
          2.1. Si la respuesta tiene estado ERROR, retorna un ApplicationResponse de error.
          3. Llama a process_output para procesar la respuesta final.está perfecto asi

        
        Args:
            data_type (DataProcessingType): Tipo de datos procesados (text/audio)
            llm_type (LLMProvider): Proveedor LLM seleccionado
            input_data (DataProcessingRequest): DTO con datos de entrada validados
        
        Returns:
            ApplicationResponse: Respuesta final con el resultado del proceso.
        """
        logger.info("Iniciando el proceso de ChatProcessor.")
        try:
            # 1. Procesar la entrada
            llm_request = self.process_input(input_data)
            if llm_request.status == StatusCode.ERROR:
                logger.warning("Error al procesar la entrada; se aborta el proceso.")
                return ApplicationResponse(
                    data_type=data_type,
                    llm_type=llm_type,
                    generated_text=llm_request.user_input,
                    status=llm_request.status,
                    message=llm_request.message
                )
            
            # 2. Enviar la solicitud al LLM
            llm_response = self.send_data(llm_request)
            if llm_response.status == StatusCode.ERROR:
                logger.warning("Error recibido del LLM; se aborta el proceso.")
                return ApplicationResponse(
                    data_type=data_type,
                    llm_type=llm_type,
                    generated_text=llm_response.generated_text,
                    status=llm_response.status,
                    message=llm_request.user_input
                )
            
            # 3. Procesar la salida del LLM
            final_output = self.process_output(llm_response)
            return ApplicationResponse(
                data_type=data_type,
                llm_type=llm_type,
                generated_text=final_output.generated_text,
                status=final_output.status,
                message=llm_request.user_input
            )
        except Exception as e:
            logger.exception("Error en ChatProcessor: %s", e)
            return ApplicationResponse(
                data_type=data_type,
                llm_type=llm_type,
                generated_text=None,
                status=StatusCode.ERROR,
                message=f"Error en el procesamiento: {str(e)}"
            )

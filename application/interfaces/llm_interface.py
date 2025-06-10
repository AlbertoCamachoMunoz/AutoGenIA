from abc import ABC, abstractmethod
from application.dtos.llm_app_request import LLMAppRequest
from application.dtos.llm_app_response import LLMAppResponse

class LLMInterface(ABC):
    """
    Interfaz que define el contrato para los servicios de modelos de lenguaje (LLM).

    Esta interfaz forma parte de la capa de **Application**, y define la estructura 
    que deben seguir las implementaciones de servicios de modelos de lenguaje en la 
    capa de **Infrastructure**.

    Las implementaciones de esta interfaz se encuentran en la capa **Infrastructure**,
    donde se encargan de interactuar con diferentes proveedores de modelos de lenguaje (LLM),
    como LLM Studio, OpenAI, Gemini, entre otros.

    Métodos abstractos:
        - send_data(request: LLMAppRequest) -> LLMAppResponse: Envia datos a un LLM y devuelve la respuesta.
    """

    @abstractmethod
    def send_data(self, request: LLMAppRequest) -> LLMAppResponse:
        """
        Envía datos a un modelo de lenguaje (LLM) y obtiene una respuesta procesada.

        Args:
            request (LLMAppRequest): Objeto DTO que contiene la entrada del usuario y 
                                     cualquier contexto adicional necesario.

        Returns:
            LLMAppResponse: Respuesta generada por el modelo de lenguaje, encapsulada 
                            en un DTO para mantener coherencia en la aplicación.
        """
        pass

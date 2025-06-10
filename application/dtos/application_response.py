from application.enums.data_processing_type import DataProcessingType
from application.enums.llm_provider import LLMProvider
from application.enums.status_code import StatusCode

class ApplicationResponse:
    """
    DTO que representa la respuesta generada por el LLM.

    Esta clase encapsula la respuesta final que será devuelta a la aplicación, incluyendo el tipo de dato procesado, 
    el tipo de LLM utilizado, el texto generado, el estado de la operación y un mensaje descriptivo.

    Attributes:
        data_type (str): Tipo de datos de entrada procesados (por ejemplo, "text" o "audio").
        llm_type (str): Tipo de modelo LLM utilizado (por ejemplo, "llm_studio" o "llm_gemini").
        generated_text (str): Texto generado por el LLM.
        status (StatusCode): Estado de la respuesta basado en el Enum StatusCode (SUCCESS o ERROR).
        message (str): Mensaje descriptivo del resultado de la operación (por defecto "OK").
    """

    def __init__(self, data_type: DataProcessingType, llm_type: LLMProvider, generated_text: str, status: StatusCode, message: str = "OK"):
        """
        Inicializa una instancia de ApplicationResponse con la información del resultado de la operación.

        Args:
            data_type (str): Tipo de datos de entrada procesados.
            llm_type (str): Tipo de modelo LLM utilizado.
            generated_text (str): Texto generado por el LLM.
            status (StatusCode): Estado de la respuesta, debe ser una instancia del Enum StatusCode (por ejemplo, 
                                 StatusCode.SUCCESS o StatusCode.ERROR).
            message (str, optional): Mensaje descriptivo del estado de la respuesta. Por defecto es "OK".

        """
        self.data_type = data_type
        self.llm_type = llm_type
        self.generated_text = generated_text
        self.status = status  
        self.message = message  

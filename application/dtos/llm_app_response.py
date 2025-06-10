from application.enums.status_code import StatusCode

class LLMAppResponse:
    """
    DTO que representa la respuesta generada por el LLM.
    
    Attributes:
        generated_text (str): Texto generado por el LLM.
        status (StatusCode): Estado de la respuesta basado en el Enum StatusCode.
        message (str): Mensaje opcional que describe el estado.
    """

    def __init__(self, generated_text: str, status: StatusCode, message: str = "OK"):
        """
        Inicializa la respuesta del LLM, validando el tipo de estado.

        Args:
            generated_text (str): Texto generado por el LLM.
            status (StatusCode): Estado de la respuesta, debe ser una instancia de StatusCode (SUCCESS o ERROR).
            message (str, optional): Mensaje descriptivo del estado. Por defecto es "OK".
        """
        self.generated_text = generated_text
        self.status = status  # Se almacena como su valor numérico (1 o -1)
        self.message = message  # Mensaje de estado

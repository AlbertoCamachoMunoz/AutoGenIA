from application.enums.status_code import StatusCode

class LLMAppRequest:
    """
    DTO (Data Transfer Object) para representar una solicitud a un modelo de lenguaje (LLM).

    Esta clase encapsula la entrada proporcionada por el usuario junto con un estado, un mensaje 
    descriptivo y un contexto opcional. Es utilizada para enviar solicitudes al modelo de lenguaje.
    """

    def __init__(self, user_input: str, status: StatusCode, message: str, context: dict = None):
        """
        Inicializa una instancia de LLMAppRequest.

        Args:
            user_input (str): La entrada de texto proporcionada por el usuario para la consulta al LLM.
            status (StatusCode): El estado asociado a la solicitud, basado en el Enum StatusCode 
                                 (por ejemplo, SUCCESS o ERROR).
            message (str): Un mensaje descriptivo relacionado con el estado o información adicional.
            context (dict, optional): Diccionario opcional que contiene datos de contexto adicionales 
                                      para la solicitud. Si no se proporciona, se utiliza un diccionario vacío.
        """
        self.user_input = user_input
        self.context = context or {}
        self.status = status
        self.message = message

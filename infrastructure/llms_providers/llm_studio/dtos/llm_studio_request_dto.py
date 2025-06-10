class LLMStudioRequestDTO:
    """
    Data Transfer Object (DTO) para enviar solicitudes a LLM Studio.
    
    Attributes:
        prompt (str): El mensaje o entrada que se enviará al modelo.
        max_tokens (int): Número máximo de tokens permitidos en la respuesta.
    """
    
    def __init__(self, prompt: str, max_tokens: int = 100):
        """
        Inicializa una instancia de LLMStudioRequestDTO.
        
        Args:
            prompt (str): Texto de entrada para el modelo.
            max_tokens (int, optional): Límite de tokens para la respuesta. Por defecto es 100.
        """
        self.prompt = prompt
        self.max_tokens = max_tokens

    def to_json(self) -> dict:
        """
        Convierte el DTO en un diccionario con la estructura requerida para la solicitud JSON.
        
        Returns:
            dict: Diccionario que representa la solicitud para LLM Studio.
        """
        return {
            "prompt": self.prompt,
            "max_tokens": self.max_tokens
        }

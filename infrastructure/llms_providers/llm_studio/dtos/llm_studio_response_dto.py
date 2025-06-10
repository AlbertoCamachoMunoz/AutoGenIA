class LLMStudioChoiceDTO:
    """
    Data Transfer Object (DTO) que representa una opción individual de la respuesta de LLM Studio.
    
    Attributes:
        index (int): Índice de la opción en la lista de resultados.
        text (str): Texto generado para esta opción.
        logprobs: Información de probabilidades logarítmicas asociadas a la opción (puede ser None).
        finish_reason (str): Motivo por el cual se terminó la generación (por ejemplo, 'stop').
    """
    
    def __init__(self, index: int, text: str, logprobs, finish_reason: str):
        """
        Inicializa una instancia de LLMStudioChoiceDTO.
        
        Args:
            index (int): Índice de la opción.
            text (str): Texto generado para esta opción.
            logprobs: Probabilidades logarítmicas asociadas a la opción (puede ser None).
            finish_reason (str): Motivo por el cual se finalizó la generación.
        """
        self.index = index
        self.text = text
        self.logprobs = logprobs
        self.finish_reason = finish_reason


class LLMStudioUsageDTO:
    """
    Data Transfer Object (DTO) que encapsula la información del uso de tokens en la respuesta de LLM Studio.
    
    Attributes:
        prompt_tokens (int): Número de tokens usados en el prompt.
        completion_tokens (int): Número de tokens usados en la respuesta generada.
        total_tokens (int): Número total de tokens utilizados (suma de prompt y completion).
    """
    
    def __init__(self, prompt_tokens: int, completion_tokens: int, total_tokens: int):
        """
        Inicializa una instancia de LLMStudioUsageDTO.
        
        Args:
            prompt_tokens (int): Tokens utilizados en el prompt.
            completion_tokens (int): Tokens utilizados en la respuesta generada.
            total_tokens (int): Tokens totales utilizados.
        """
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens


class LLMStudioResponseDTO:
    """
    Data Transfer Object (DTO) que representa la respuesta completa recibida de LLM Studio.
    
    Attributes:
        id (str): Identificador único de la respuesta.
        object_ (str): Tipo de objeto devuelto por la API.
        created (int): Marca temporal (timestamp) de cuando se creó la respuesta.
        model (str): Modelo utilizado para generar la respuesta.
        choices (list): Lista de instancias de LLMStudioChoiceDTO que representan las opciones generadas.
        usage (LLMStudioUsageDTO): Información sobre el uso de tokens en la respuesta.
        stats (dict): Estadísticas adicionales o información extra proporcionada por la API.
    """
    
    def __init__(
        self,
        id: str,
        object_: str,
        created: int,
        model: str,
        choices: list,
        usage: LLMStudioUsageDTO,
        stats: dict,
    ):
        """
        Inicializa una instancia de LLMStudioResponseDTO.
        
        Args:
            id (str): Identificador único de la respuesta.
            object_ (str): Tipo de objeto devuelto por la API.
            created (int): Marca temporal de la creación de la respuesta (timestamp).
            model (str): Modelo que generó la respuesta.
            choices (list): Lista de opciones (instancias de LLMStudioChoiceDTO).
            usage (LLMStudioUsageDTO): Detalles sobre el uso de tokens.
            stats (dict): Información adicional o estadísticas proporcionadas por la API.
        """
        self.id = id
        self.object_ = object_
        self.created = created
        self.model = model
        self.choices = choices
        self.usage = usage
        self.stats = stats
        
    @staticmethod
    def empty() -> 'LLMStudioResponseDTO':
        """
        Crea un DTO vacío válido para casos de error.
        """
        return LLMStudioResponseDTO(
            id="",
            object_="",
            created=0,
            model="",
            choices=[],
            usage=LLMStudioUsageDTO(0, 0, 0),
            stats={}
        )    


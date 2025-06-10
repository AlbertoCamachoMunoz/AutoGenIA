from typing import List
from google.genai import types

class GeminiRequestDTO:
    """
    Data Transfer Object (DTO) para enviar solicitudes a la API de Gemini.

    Este objeto encapsula los datos necesarios para realizar una petición a la API de Gemini,
    incluyendo el modelo a utilizar, los contenidos que conforman la solicitud y la configuración
    para la generación de contenido.

    Attributes:
        model (str): Nombre o identificador del modelo de lenguaje a utilizar.
        contents (List[types.Content]): Lista de objetos Content que contienen el contenido (p.ej., texto)
                                        que se enviará al modelo.
        config (types.GenerateContentConfig): Configuración para la generación de contenido, que puede incluir
                                              parámetros como temperatura, top_p, top_k, entre otros.
    """

    def __init__(self, model: str, contents: List[types.Content], config: types.GenerateContentConfig):
        """
        Inicializa una nueva instancia de GeminiRequestDTO.

        Args:
            model (str): Nombre o identificador del modelo de lenguaje a utilizar.
            contents (List[types.Content]): Lista de contenidos que se enviarán al modelo.
            config (types.GenerateContentConfig): Configuración de generación de contenido.
        """
        self.model = model
        self.contents = contents
        self.config = config

from dataclasses import dataclass
from typing import List, Optional
from application.enums.status_code import StatusCode


@dataclass
class EmailAgentRequest:

    def __init__(self, generated_text: str, status: StatusCode, message: str = "OK"):
        """
        Inicializa la respuesta del LLM, validando el tipo de estado.

        Args:
            generated_text (str): Texto generado por el LLM.
            status (StatusCode): Estado de la respuesta, debe ser una instancia de StatusCode (SUCCESS o ERROR).
            message (str, optional): Mensaje descriptivo del estado. Por defecto es "OK".
        """
        self.status = status  # Se almacena como su valor numérico (1 o -1)
        self.message = message  # Mensaje de estado
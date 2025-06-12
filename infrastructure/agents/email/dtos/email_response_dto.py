from enum import Enum
from dataclasses import dataclass
from application.enums.status_code import StatusCode

@dataclass
class EmailResponseDTO:
    """
    DTO que representa una respuesta tras intentar enviar un correo.
    
    Attributes:
        status (StatusCode): Estado del envío (éxito o fallo).
        message (str): Mensaje descriptivo del resultado.
        delivered_to (str): Dirección a la que se intentó enviar (opcional).
    """
    status: StatusCode
    message: str = "OK"
    delivered_to: str = ""
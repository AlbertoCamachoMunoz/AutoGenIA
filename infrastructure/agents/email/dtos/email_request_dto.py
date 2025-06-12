from dataclasses import dataclass
from typing import Any
from application.enums.status_code import StatusCode

@dataclass
class EmailRequestDTO:
    """
    DTO que encapsula los datos necesarios para enviar un correo electrónico.
    
    Attributes:
        to (str): Dirección de correo del destinatario.
        subject (str): Asunto del correo.
        body (str): Contenido principal del mensaje.
    """
    to: str
    subject: str
    body: str
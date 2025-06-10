from enum import Enum

class StatusCode(Enum):
    """
    Enum que define los códigos de estado estándar utilizados en las respuestas.

    Attributes:
        SUCCESS (int): Representa una operación exitosa (valor 1).
        ERROR (int): Representa una operación que ha fallado o con error (valor -1).
    """
    SUCCESS =  1    
    ERROR   = -1  

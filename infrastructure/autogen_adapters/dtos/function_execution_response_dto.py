# infrastructure/autogen_adapters/dtos/function_execution_response_dto.py
from enum import Enum
from dataclasses import dataclass

class FunctionExecutionStatus(Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"

@dataclass
class FunctionExecutionResponseDTO:
    name: str
    content: str
    status: FunctionExecutionStatus
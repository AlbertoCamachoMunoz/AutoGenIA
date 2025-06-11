# infrastructure/autogen_adapters/dtos/function_execution_request_dto.py
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class FunctionExecutionRequestDTO:
    name: str
    arguments: Dict[str, Any]
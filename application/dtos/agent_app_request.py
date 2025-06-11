# application/dtos/agent_app_request.py
from dataclasses import dataclass
from typing import Any

@dataclass
class AgentAppRequest:
    input_data: Any  # Puede ser texto, JSON, etc., dependiendo del agente
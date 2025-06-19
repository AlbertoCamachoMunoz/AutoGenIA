# application/interfaces/agent_interface.py

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse
from application.interfaces.llm_interface import LLMInterface


class AgentInterface(ABC):
    @abstractmethod
    def __init__(self, provider: Optional[LLMInterface] = None):
        pass

    @abstractmethod
    def get_function_name(cls) -> str:
        pass

    @abstractmethod
    def get_function_description(cls) -> str:
        pass

    @abstractmethod
    def get_function_list(cls) -> list:
        pass

    @abstractmethod
    def get_llm_config(self) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_llm_prompt(self) -> Optional[str]:
        pass
    
    @abstractmethod
    def execute_function(self, request: AgentAppRequest) -> AgentAppResponse:
        pass



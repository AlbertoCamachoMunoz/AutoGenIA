# application/interfaces/agent_interface.py
from abc import ABC, abstractmethod
from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse

class AgentInterface(ABC):
    @abstractmethod
    def run(self, request: AgentAppRequest) -> AgentAppResponse:
        pass

    @classmethod
    @abstractmethod
    def get_function_list(cls) -> list:
        pass
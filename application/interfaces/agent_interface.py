# application/interfaces/agent_interface.py
from abc import ABC, abstractmethod
from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse

class AgentInterface(ABC):

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
    def run(self, request: AgentAppRequest) -> AgentAppResponse:
        pass


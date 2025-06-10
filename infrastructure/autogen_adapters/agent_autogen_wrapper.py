from autogen.agentchat import AssistantAgent
from application.interfaces.agent_interface import AgentInterface


class AgentAutoGenWrapper(AssistantAgent):
    """
    Adaptador que envuelve un agente funcional propio y lo convierte en un AssistantAgent de AutoGen.
    """

    def __init__(self, name: str, agent: AgentInterface):
        super().__init__(
            name=name,
            # llm_config={"config_list": [], "functions": [], "temperature": 0},  # No usa LLM
            llm_config=False,  # o explícitamente None
            system_message="Agente funcional sin LLM.",
        )
        self._agent = agent

    def execute_function(self, function_call, **kwargs):
        input_str = function_call.get("arguments", {}).get("input", "")
        result = self._agent.run(input_str)
        return result

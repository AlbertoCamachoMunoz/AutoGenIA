# infrastructure/autogen_agents/closure_agent.py

from autogen.agentchat import AssistantAgent

class ClosureAgent(AssistantAgent):
    def __init__(self, get_json_func):
        """
        get_json_func: función que retorna el JSON que debe devolverse al cerrar la conversación.
        """
        super().__init__(
            name="closure_agent",
            system_message="Devuelve SOLO el JSON resultado de la traducción, sin ningún texto extra, ni saludo, ni explicación.",
        )
        self.get_json_func = get_json_func

    def generate_reply(self, *args, **kwargs):
        json_result = self.get_json_func()
        if json_result:
            return json_result
        return '{"status":"ERROR","message":"No result found"}'

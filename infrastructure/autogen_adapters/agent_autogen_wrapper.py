# infrastructure/autogen_adapters/agent_autogen_wrapper.py

import json
from autogen.agentchat import AssistantAgent
from application.interfaces.agent_interface import AgentInterface
from application.dtos.agent_app_request import AgentAppRequest


class AgentAutoGenWrapper(AssistantAgent):
    """
    Adaptador que envuelve un agente funcional (implementa AgentInterface)
    como un AssistantAgent de AutoGen, permitiendo su uso como ejecutor de funciones.
    """

    def __init__(self, name: str, agent: AgentInterface):
        super().__init__(
            name=name,
            llm_config=False,  # No usa LLM
            system_message=f"Wrapper del agente funcional «{name}».",
            human_input_mode="NEVER"
        )
        self._agent = agent

    def execute_function(self, function_call, **kwargs):
        print(f"[DEBUG] Ejecutando execute_function en {self.name} con:", function_call)

        try:
            if isinstance(function_call, str):
                function_call = json.loads(function_call)

            arguments = function_call.get("arguments", {})
            if isinstance(arguments, str):
                arguments = json.loads(arguments)

            input_str = arguments.get("title", "")
            if not input_str:
                raise ValueError("No se encontró el campo 'title' en los argumentos")

            print(f"[DEBUG] Ejecutando acción con entrada: {input_str}")

            result = self._agent.run(AgentAppRequest(input_data=input_str))

            # ✅ Se devuelve una tupla: (final, resultado)
            return True, {
                "name": self.name,
                "content": result.content
            }

        except json.JSONDecodeError as e:
            return True, {
                "name": self.name,
                "content": f"[ERROR JSON] {str(e)}"
            }

        except Exception as e:
            return True, {
                "name": self.name,
                "content": f"[ERROR interno] {str(e)}"
            }

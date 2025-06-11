# infrastructure/autogen_adapters/agent_autogen_wrapper.py

import json
from autogen.agentchat import AssistantAgent
from application.interfaces.agent_interface import AgentInterface


class AgentAutoGenWrapper(AssistantAgent):
    """
    Adaptador que envuelve un agente funcional (que implementa AgentInterface)
    dentro de un AssistantAgent de AutoGen, permitiendo su uso como ejecutor de funciones.
    
    Este wrapper permite integrar agentes funcionales (sin LLM) en flujos de trabajo de AutoGen,
    manteniendo el contrato definido por AgentInterface.
    """

    def __init__(self, name: str, agent: AgentInterface):
        """
        Inicializa el wrapper del agente.

        Args:
            name (str): Nombre del agente para identificación en el chat.
            agent (AgentInterface): Instancia del agente funcional a envolver.
        """
        super().__init__(
            name=name,
            llm_config=False,  # No tiene LLM propio, solo se usa como ejecutor
            system_message=f"Wrapper del agente «{name}».",
            human_input_mode="NEVER"
        )
        self._agent = agent

    def execute_function(self, function_call, **kwargs):
        """
        Método llamado por AutoGen cuando se invoca una función asignada a este agente.

        Args:
            function_call (Union[str, dict]): Puede ser un string JSON o un diccionario con la llamada.

        Returns:
            dict: Respuesta estructurada que AutoGen entiende.
        """
        print(f"[DEBUG] Ejecutando execute_function en {self.name} con:", function_call)

        try:
            # Si es cadena, intentamos parsearla como JSON
            if isinstance(function_call, str):
                function_call = json.loads(function_call)

            # Extraemos los argumentos
            arguments = function_call.get("arguments", {})
            if isinstance(arguments, str):
                arguments = json.loads(arguments)

            input_str = arguments.get("title", "")
            if not input_str:
                raise ValueError("No se encontró el campo 'title' en los argumentos")

            print(f"[DEBUG] Ejecutando acción con entrada: {input_str}")

            # Llamamos al agente real
            result = self._agent.run(input_str)

            return {
                "name": self.name,
                "content": {
                    "result": result,
                    "status": "SUCCESS"
                }
            }

        except json.JSONDecodeError as e:
            error_msg = f"Error al decodificar JSON: {str(e)}"
            print("[ERROR]", error_msg)
            return {
                "name": self.name,
                "content": {
                    "result": "",
                    "status": "ERROR",
                    "message": error_msg
                }
            }

        except Exception as e:
            error_msg = f"Error interno: {str(e)}"
            print("[ERROR]", error_msg)
            return {
                "name": self.name,
                "content": {
                    "result": "",
                    "status": "ERROR",
                    "message": error_msg
                }
            }
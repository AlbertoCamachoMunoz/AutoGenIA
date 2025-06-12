# infrastructure/agents/email/email_agent.py

from application.interfaces.agent_interface import AgentInterface


class EmailAgent(AgentInterface):

    @classmethod
    def get_function_name(cls) -> str:
        return "email_send"

    @classmethod
    def get_function_description(cls) -> str:
        return "Envía un email."

    @classmethod
    def get_function_list(cls) -> list:
        return [
            {
                "name": "send_email",
                "description": "Envía un correo electrónico.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"}
                    },
                    "required": ["to", "subject", "body"]
                }
            }
        ]
    
    def run(self, input_data: str) -> str:
        try:
            # Extracción simple de destinatario y mensaje (solo para pruebas)
            if "@" not in input_data:
                return "[EmailAgent] Error: No se encontró dirección de email válida."

            parts = input_data.split(":")
            if len(parts) < 2:
                return "[EmailAgent] Error: No se encontró cuerpo del mensaje."

            address = parts[0].split()[-1].strip()
            body = parts[1].strip()

            # Simula el envío
            print(f"[EmailAgent] → Simulando envío a {address} con contenido:\n{body}\n")
            return f"Email enviado correctamente a {address}.\nTERMINATE"

        except Exception as e:
            return f"[EmailAgent] Error inesperado: {str(e)}\nTERMINATE"

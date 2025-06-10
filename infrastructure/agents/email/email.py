# infrastructure/agents/email/email_agent.py

from application.interfaces.agent_interface import AgentInterface


class EmailAgent(AgentInterface):
    """
    Agente funcional que simula el envío de un correo electrónico.

    Espera un input del tipo:
    "Send this to email prueba@dominio.com: Einstein was a physicist born in 1879..."
    """

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

# infrastructure/agents/email/email_agent.py

from typing import Optional
from application.interfaces.llm_interface import LLMInterface
from application.interfaces.agent_interface import AgentInterface
from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse
from infrastructure.agents.email.mappers.email_mapper import EmailMapper
from infrastructure.agents.email.services.smtp_service import SmtpService
from infrastructure.agents.email.dtos.email_response_dto import EmailResponseDTO
from application.enums.status_code import StatusCode
import smtplib
from email.message import EmailMessage


class EmailAgent(AgentInterface):
    def __init__(self, provider: Optional[LLMInterface] = None):
        self.provider = provider

    @classmethod
    def get_function_name(cls) -> str:
        return "send_email"

    @classmethod
    def get_function_description(cls) -> str:
        return "Envía un correo electrónico utilizando Mailtrap."

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
                        "body": {"type": "string"},
                    },
                    "required": ["to", "subject", "body"],
                },
            }
        ]
    
    def get_llm_config(self) -> None:
        return None
    
    def get_llm_prompt(self) -> None:
        return None
    
    def execute_function(self, request: AgentAppRequest) -> AgentAppResponse:
        try:
            print("[EmailAgent] → Iniciando proceso de envío de correo...")
            print(f"[EmailAgent] Contenido recibido: {request.content}")

            email_request = EmailMapper.map_request(request)

            print("[EmailAgent] Datos parseados:", email_request)
            print(f"   To: {email_request.to}")
            print(f"   Subject: {email_request.subject}")
            print(f"   Body: {email_request.body}")

            smtp_service = SmtpService()
            email_response = smtp_service.send_email(email_request)

            print("[EmailAgent] Respuesta del servicio SMTP:")
            print(f"   Status: {email_response.status}")
            print(f"   Message: {email_response.message}")

            return EmailMapper.map_response(email_response)

        except ValueError as ve:
            print(f"[EmailAgent] Error de validación: {ve}")
            return EmailMapper.map_response(
                EmailResponseDTO(status=StatusCode.ERROR, message=str(ve))
            )
        except Exception as e:
            print(f"[EmailAgent] Error interno: {e}")
            return EmailMapper.map_response(
                EmailResponseDTO(status=StatusCode.ERROR, message=f"Error interno: {str(e)}")
            )


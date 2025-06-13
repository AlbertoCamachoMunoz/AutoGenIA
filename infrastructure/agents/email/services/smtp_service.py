# smtp_service.py
import smtplib
import logging
from email.message import EmailMessage

from config.settings import (
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    SMTP_FROM_EMAIL,
)
from infrastructure.agents.email.dtos.email_request_dto import EmailRequestDTO
from infrastructure.agents.email.dtos.email_response_dto import EmailResponseDTO
from application.enums.status_code import StatusCode   # ← enum real

# Configuración del logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class SmtpService:
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.smtp_user = SMTP_USERNAME
        self.smtp_password = SMTP_PASSWORD
        self.smtp_from_email = SMTP_FROM_EMAIL

    def send_email(self, request: EmailRequestDTO) -> EmailResponseDTO:
        logger.debug("[SmtpService] Preparando correo...")
        logger.debug(f"[SmtpService] Destinatario: {request.to}")
        logger.debug(f"[SmtpService] Asunto: {request.subject}")
        logger.debug(f"[SmtpService] Cuerpo: {request.body}")

        msg = EmailMessage()
        msg.set_content(request.body)
        msg["Subject"] = request.subject
        msg["From"] = self.smtp_from_email
        msg["To"] = request.to

        try:
            logger.debug(
                f"[SmtpService] Conectando a {self.smtp_server}:{self.smtp_port}"
            )
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                logger.debug("[SmtpService] Iniciando sesión SMTP...")
                server.login(self.smtp_user, self.smtp_password)
                logger.debug("[SmtpService] Enviando correo...")
                server.send_message(msg)

            logger.info("[SmtpService] Correo enviado a %s", request.to)
            return EmailResponseDTO(
                status=StatusCode.SUCCESS,                         # enum, no string
                message=f"Correo enviado correctamente a {request.to}",
                delivered_to=request.to,
            )
        except Exception as e:
            logger.exception("[SmtpService] Error al enviar el correo:")
            return EmailResponseDTO(
                status=StatusCode.ERROR,                           # enum, no string
                message=f"Fallo al enviar correo: {str(e)}",
                delivered_to=request.to,
            )

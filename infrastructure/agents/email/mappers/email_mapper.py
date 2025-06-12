from infrastructure.agents.email.dtos.email_request_dto import EmailRequestDTO
from infrastructure.agents.email.dtos.email_response_dto import EmailResponseDTO
from application.dtos.agent_app_request import AgentAppRequest
from application.dtos.agent_app_response import AgentAppResponse
from application.enums.status_code import StatusCode

class EmailMapper:
    @staticmethod
    def map_request(app_request: AgentAppRequest) -> EmailRequestDTO:
        """
        Mapea una solicitud de aplicación a un DTO específico para el agente de email.
        
        Args:
            app_request (AgentAppRequest): Solicitud base desde la interfaz de usuario.
        Returns:
            EmailRequestDTO: DTO con campos parseados como 'to', 'subject' y 'body'.
        Raises:
            ValueError: Si no se pueden extraer todos los campos necesarios.
        """
        # Ejemplo de formato esperado: "Send this to c4max0@gmail.com: Este es el cuerpo..."
        if "@" not in app_request.input_data:
            raise ValueError("No se encontró una dirección de correo válida en input_data")
        
        parts = app_request.input_data.split(":")
        if len(parts) < 2:
            raise ValueError("Falta contenido del mensaje en input_data")

        raw_address_part = parts[0].strip()
        raw_body = parts[1].strip()

        # Extraer dirección de correo
        to = None
        for word in raw_address_part.split():
            if "@" in word:
                to = word
                break
        if not to:
            raise ValueError("No se pudo extraer una dirección de correo válido")

        # Suponer asunto genérico si no está presente (mejorar con parser real más adelante)
        subject = f"Mensaje de {to}"

        return EmailRequestDTO(to=to, subject=subject, body=raw_body)

    @staticmethod
    def map_response(dto: EmailResponseDTO) -> AgentAppResponse:
        """
        Convierte un EmailResponseDTO en un AgentAppResponse genérico.
        
        Args:
            dto (EmailResponseDTO): Respuesta interna del sistema de email.
        Returns:
            AgentAppResponse: DTO listo para usar por la capa de aplicación.
        """
        return AgentAppResponse(
            content=dto.message,
            status=dto.status,
            message=dto.message
        )
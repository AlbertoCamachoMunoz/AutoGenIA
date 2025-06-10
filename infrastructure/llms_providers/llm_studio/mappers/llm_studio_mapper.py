from typing import Dict, Any
from application.dtos.llm_app_response import LLMAppResponse
from application.dtos.llm_app_request import LLMAppRequest
from application.enums.status_code import StatusCode
from infrastructure.llms_providers.llm_studio.dtos.llm_studio_request_dto import LLMStudioRequestDTO
from infrastructure.llms_providers.llm_studio.dtos.llm_studio_response_dto import (
    LLMStudioChoiceDTO,
    LLMStudioResponseDTO,
    LLMStudioUsageDTO
)

class LLMStudioMapper:
    """
    Mapper que traduce entre los DTOs de la aplicación y el formato de datos utilizado por LLM Studio.
    """

    @staticmethod
    def map_request(app_request: LLMAppRequest) -> LLMStudioRequestDTO:
        """
        Transforma una instancia de LLMAppRequest en un LLMStudioRequestDTO.

        Args:
            app_request (LLMAppRequest): La solicitud de la aplicación.

        Returns:
            LLMStudioRequestDTO: La solicitud formateada para LLM Studio.
        """
        return LLMStudioRequestDTO(
            prompt=app_request.user_input,
            max_tokens=100
        )

    @staticmethod
    def map_response(dto: LLMStudioResponseDTO, status_code: int, message: str) -> LLMAppResponse:
        """
        Transforma una respuesta recibida de LLM Studio (como DTO interno) en una instancia de LLMAppResponse.

        Args:
            dto (LLMStudioResponseDTO): El DTO de respuesta obtenido del JSON.
            status_code (int): Código de estado (puede ser HTTP o interno).
            message (str): Mensaje descriptivo del estado de la respuesta.

        Returns:
            LLMAppResponse: La respuesta mapeada para la aplicación.
        """
        # Validar que se haya recibido al menos una opción.
        generated_text = dto.choices[0].text if dto.choices and len(dto.choices) > 0 else ""
        return LLMAppResponse(
            generated_text=generated_text,
            status=StatusCode(status_code),  # Convertimos el int a StatusCode
            message=message
        )
    
    @staticmethod
    def json_to_dto(response_json: Dict[str, Any]) -> LLMStudioResponseDTO:
        """
        Mapea una respuesta JSON (decodificada en un diccionario) a un objeto LLMStudioResponseDTO.

        Args:
            response_json (Dict[str, Any]): La respuesta en formato JSON.

        Returns:
            LLMStudioResponseDTO: Un objeto DTO que encapsula la respuesta de LLM Studio.
        """
        return LLMStudioResponseDTO(
            id=response_json.get("id", ""),
            object_=response_json.get("object", ""),
            created=response_json.get("created", 0),
            model=response_json.get("model", ""),
            choices=[
                LLMStudioChoiceDTO(
                    index=choice.get("index", 0),
                    text=choice.get("text", ""),
                    logprobs=choice.get("logprobs", None),
                    finish_reason=choice.get("finish_reason", "")
                )
                for choice in response_json.get("choices", [])
            ],
            usage=LLMStudioUsageDTO(
                prompt_tokens=response_json.get("usage", {}).get("prompt_tokens", 0),
                completion_tokens=response_json.get("usage", {}).get("completion_tokens", 0),
                total_tokens=response_json.get("usage", {}).get("total_tokens", 0)
            ),
            stats=response_json.get("stats", {})
        )

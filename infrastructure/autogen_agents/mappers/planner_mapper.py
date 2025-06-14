# infrastructure/autogen_agents/mappers/planner_mapper.py
from typing import Any

from application.dtos.planner_app_request import PlannerAppRequest
from application.dtos.planner_app_response import PlannerAppResponse
from application.enums.status_code import StatusCode


class PlannerMapper:
    @staticmethod
    def map_request(app_request: PlannerAppRequest) -> dict:
        """
        Mapea desde PlannerAppRequest hacia un dict compatible con AutoGen.
        """
        return {
            "content": app_request.content,
            "status": getattr(app_request, "status", StatusCode.SUCCESS),
            "message": getattr(app_request, "message", "OK"),
        }

    @staticmethod
    def _parse_status(raw_status: Any) -> StatusCode:
        """
        Acepta StatusCode, int o str ("SUCCESS"/"ERROR") y devuelve el Enum.
        """
        if isinstance(raw_status, StatusCode):
            return raw_status
        if isinstance(raw_status, int):
            return StatusCode(raw_status)
        if isinstance(raw_status, str):
            return StatusCode[raw_status.upper()]
        return StatusCode.ERROR

    @staticmethod
    def map_response(planner_output: Any) -> PlannerAppResponse:
        """
        Convierte cualquier salida del planner a PlannerAppResponse.
        """
        if isinstance(planner_output, dict):
            content = planner_output.get("content", "")
            status = PlannerMapper._parse_status(
                planner_output.get("status", StatusCode.SUCCESS)
            )
            message = planner_output.get("message", "OK")

        elif isinstance(planner_output, (str, int, float)):
            content = str(planner_output)
            status = StatusCode.SUCCESS
            message = "Respuesta simple convertida a cadena"

        elif hasattr(planner_output, "__dict__"):
            content = getattr(planner_output, "content", "[sin contenido]")
            status = PlannerMapper._parse_status(
                getattr(planner_output, "status", StatusCode.SUCCESS)
            )
            message = getattr(planner_output, "message", "OK")

        else:
            content = "[sin respuesta]"
            status = StatusCode.ERROR
            message = "Formato de salida no compatible"

        return PlannerAppResponse(content=content, status=status, message=message)

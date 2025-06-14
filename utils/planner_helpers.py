# utils/planner_helpers.py
from typing import List, Dict, Any

from application.enums.status_code import StatusCode
from application.dtos.planner_app_response import PlannerAppResponse
from infrastructure.autogen_agents.mappers.planner_mapper import PlannerMapper


def last_planner_response(messages: List[Dict[str, Any]]) -> PlannerAppResponse:
    """
    Devuelve el último mensaje del role 'planner' como PlannerAppResponse.
    Si no existe tal mensaje, retorna un DTO con ERROR.
    """
    raw = next((m for m in reversed(messages) if m.get("role") == "planner"), None)

    if raw is None:
        return PlannerAppResponse(
            content="[sin respuesta del planner]",
            status=StatusCode.ERROR,
            message="No se encontró mensaje del planner",
        )

    return PlannerMapper.map_response(raw)

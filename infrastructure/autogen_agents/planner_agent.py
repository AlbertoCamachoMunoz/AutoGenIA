# infrastructure/autogen_agents/planner_agent.py
from typing import Any, Callable
from autogen.agentchat import AssistantAgent
from application.interfaces.llm_interface import LLMInterface
from infrastructure.autogen_agents.mappers.planner_mapper import PlannerMapper
from application.dtos.planner_app_response import PlannerAppResponse


class PlannerAgentFactory:
    """
    Planner estricto: sólo genera llamadas de herramienta válidas.
    """

    # ───────────────────────── PUBLIC ─────────────────────────
    @staticmethod
    def create(
        llm_provider: LLMInterface,
        functions: list | None = None,
    ) -> AssistantAgent:
        if functions is None:
            functions = []

        llm_config = {
            "config_list": [{
                "model":    llm_provider.get_model_name(),
                "base_url": llm_provider.get_base_url(),
                "api_key":  llm_provider.get_api_key(),
                "price":   [0.0, 0.0],
            }],
            "temperature": 0.0,        # <-- cero para que no “invente” texto
            "timeout":     160,
            "functions":   functions,  # ← lista contiene web_scrape, price_analyze, send_email
        }

        # ───────────────────── PROMPT ─────────────────────
        system_message = """
You are a strict workflow executor.
**Never** reply with natural language.
To invoke a tool, output **only** a JSON object exactly like:
{"name": "<tool_name>", "arguments": {<args>}}

Available tools
───────────────
• web_scrape
    • {"url": "<url>", "selector": "<css_selector>"}

• send_email
    • {"to": "<recipient>", "subject": "<subject>", "body": "<summary>"}

Workflow
────────
1. Call web_scrape **once** with the user URL and selector.
   Example:
   {"name": "web_scrape", "arguments": {"url": "<user.url>", "selector": "<user.selector>"}}

2. Build a subject (few words) and a brief summary (max. 50 words).

3. Call send_email **once**:
   {"name": "send_email", "arguments": {
       "to": "<user.email>",
       "subject": "<subject>",
       "body": "<summary>"
   }}

4. After send_email returns SUCCESS, respond exactly:
   {"content": "TERMINATE"}

Rules
─────
• One tool call per step, in order.
• NO text besides the JSON tool call.
• Do NOT call any tool except those listed.
• If anything fails, do NOT try to repair; continue and finish the workflow.
""".strip()

        is_term: Callable[[dict], bool] = lambda m: "TERMINATE" in m.get("content", "")

        return AssistantAgent(
            name="planner",
            system_message=system_message,
            llm_config=llm_config,
            max_consecutive_auto_reply=6,
            is_termination_msg=is_term,
        )

    # ───────────────────────── WRAP ─────────────────────────
    @staticmethod
    def wrap_planner_output(result: Any) -> PlannerAppResponse:
        return PlannerMapper.map_response(result)

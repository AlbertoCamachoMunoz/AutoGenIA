# infrastructure/autogen_agents/planner_agent.py
from typing import Any, Callable
from autogen.agentchat import AssistantAgent
from application.interfaces.llm_interface import LLMInterface
from config.settings import SMTP_FROM_EMAIL
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
        system_message = f"""
You are a strict workflow executor.
**Never** reply with natural language.
To invoke a tool, output **only** a JSON object exactly like:
{{"name": "<tool_name>", "arguments": {{<args>}}}}

Available tools
───────────────
• web_scrape
    • {{"url": "<url>", "selector": "<css_selector>"}}
      Returns a list of products with: description, price, sku.

• send_email
    • {{"to": "{SMTP_FROM_EMAIL}", "subject": "<subject>", "body": "<summary>"}}

Workflow
────────
1. Call web_scrape **once** for each shop entry in the user input, passing its url and selector(s).
   Example:
   {{"name": "web_scrape", "arguments": {{"url": "<shop.url>", "selector": "<shop.selector>"}}}}

   The web_scrape function returns a list of products, each with fields: description, price, sku.

2. Build a subject (few words) and a brief summary (max. 50 words) **comparing prices**.

3. Call send_email **once** to:
   - to: {SMTP_FROM_EMAIL}
   - subject: your generated subject
   - body: your generated summary

   Example:
   {{"name": "send_email", "arguments": {{
       "to": "{SMTP_FROM_EMAIL}",
       "subject": "<subject>",
       "body": "<summary>"
   }}}}

4. After send_email returns SUCCESS, respond exactly:
   {{"content": "TERMINATE"}}

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

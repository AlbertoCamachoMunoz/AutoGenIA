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
    • {{"url": "<url>", "selector_price": "<css_selector>", "selector_description": "<css_selector>", "selector_sku": {{"tag": "<tag>", "attribute": "<attr>"}}}}
      Returns a list of products with: description, price, sku.

• translate_products
    • {{"products": [{{"description": "<str>", "price": "<str>", "sku": "<str>"}}], "langs": [{{"lang": "<target_lang>"}}]}}
      Returns the list of products with all requested translations as new fields.

• send_email
    • {{"to": "<user_email>", "subject": "<subject>", "body": "<json_with_translations>"}}

Workflow
────────
1. For each shop entry in the user input, call web_scrape **once**, passing its url and selectors.
   Example:
   {{"name": "web_scrape", "arguments": {{
       "url": "<shop.url>",
       "selector_price": "<shop.selector_price>",
       "selector_description": "<shop.selector_description>",
       "selector_sku": {{"tag": "<tag>", "attribute": "<attribute>"}}
   }}}}

   web_scrape returns a list of products, each with fields: description, price, sku.

2. Collect all products. Call translate_products **once** with:
   - products: the list of all products from all shops (from step 1)
   - langs: the requested languages received in user input
   Example:
   {{"name": "translate_products", "arguments": {{
       "products": [{{"description": "...", "price": "...", "sku": "..."}}],
       "langs": [{{"lang": "EN"}}, {{"lang": "ES"}}]
   }}}}

   translate_products returns the same list of products, each with additional translation fields (e.g., description_EN).

3. Build a subject (few words) and a brief summary (max. 50 words) describing the content.
   Then call send_email **once** to:
   - to: the email address received in the initial user input
   - subject: your generated subject
   - body: a **JSON string** with all translated product information
   Example:
   {{"name": "send_email", "arguments": {{
       "to": "<user_email>",
       "subject": "<subject>",
       "body": "<json_with_translations>"
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

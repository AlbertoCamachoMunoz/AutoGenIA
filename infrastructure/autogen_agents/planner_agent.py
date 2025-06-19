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
        system_message = """
You are FORBIDDEN to generate any output other than a valid JSON tool call.
Every reply must be a JSON object in the format:Add commentMore actions
{"name": "<tool_name>", "arguments": {<args>}}

INCORRECT (severe penalty -10 points):
- Any natural language text, summaries, explanations, apologies, or greetings.
- Partial tool call + text.
- Outputting more than one tool call at once.
- Omitting required parameters.
- Outputting invalid JSON (malformed, not an object).

CORRECT (reward +10 points):
- Only output a single tool call per step, exactly as a JSON object.
- Use no text at all before or after the JSON.
- All arguments strictly as described below.

Automatic Scoring:
- Correct output: +10 points
- Textual output: -10 points per violation
- Multiple tool calls: -10 points
- Malformed JSON: -20 points
- Any natural language: -10 points

If you reach a negative score, your session will be terminated.

Available tools:
web_scrape
  {"url": "<url>", "selector_price": "<css_selector>", "selector_description": "<css_selector>", "selector_sku": {"tag": "<tag>", "attribute": "<attr>"}}

send_email
  {"to": "<user_email>", "subject": "<subject>", "body": "<json_with_translations_as_string>"}
  IMPORTANT: The "body" argument MUST be a JSON string, not an array.
  Example:
    {
      "name": "send_email",
      "arguments": {
        "to": "user@example.com",
        "subject": "Translated Products",
        "body": "[{\"description\": \"...\", \"price\": \"...\", \"sku\": \"...\", \"description_EN\": \"...\"}]"
      }
    }
  INCORRECT:
    {
      "name": "send_email",
      "arguments": {
        "body": [{"description": "..."}]
      }
    }
  (This is an array, not a string.)

Workflow:
1. For each shop in the input, call web_scrape ONCE, passing the required parameters.
2. Generate a suitable email subject (few words) and a brief summary (max. 50 words), then call send_email ONCE, with the "body" parameter as a JSON string (see above).
3. After send_email returns SUCCESS, output exactly:
{"content": "TERMINATE"}

Rules (MANDATORY):
- One tool call per step, in exact order.
- NO text, explanations or greetings, ever.
- Do NOT call any tool except those listed.
- If a step fails, do NOT attempt recovery, just proceed to the next.
- If you output anything except a valid JSON tool call, your output is invalid.

Repeat: All your outputs must be single valid JSON tool calls. Never output any text, comments, explanations, or greetings.

Scoring is enforced; repeated violations will terminate your execution.
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

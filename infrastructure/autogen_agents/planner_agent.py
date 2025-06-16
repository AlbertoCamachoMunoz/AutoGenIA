# infrastructure/autogen_agents/planner_agent.py
from typing import Any
from autogen.agentchat import AssistantAgent
from application.interfaces.llm_interface import LLMInterface
from infrastructure.autogen_agents.mappers.planner_mapper import PlannerMapper
from application.dtos.planner_app_response import PlannerAppResponse

class PlannerAgentFactory:
    @staticmethod
    def create(llm_provider: LLMInterface, functions: list | None = None) -> AssistantAgent:
        if functions is None:
            functions = []

        llm_config = {
            "config_list": [{
                "model": llm_provider.get_model_name(),
                "base_url": llm_provider.get_base_url(),
                "api_key":  llm_provider.get_api_key(),
                "price":   [0.0, 0.0],
            }],
            "temperature": 0.1,
            "timeout": 30,
            "functions": functions,
        }

        system_message = """
You are a task-oriented planner.

Available tools:
  • web_scrape(url: str, selector?: str)
  • price_analyze(pages: list)
  • send_email(to: str, subject: str, body: str)

Mandatory workflow:

1. The user provides:
     - `pages`  → list of {'url': ..., 'selector': ...}
     - `email`  → destination address.

2. For each page in `pages`, call **web_scrape** exactly once with:
       {'url': <url>, 'selector': <selector>}

3. After scraping all pages, call **price_analyze** exactly once with:
       {'pages': [{'url': <url>, 'content': <scraped_text>}, ...]}

4. Generate a subject and a plain text summary from the analysis.

5. Call **send_email** with:
       to      → the email from the user,
       subject → concise title,
       body    → the summary text.

6. After send_email returns SUCCESS, reply only **TERMINATE**.

Rules:
  • web_scrape: one call per URL, no more.
  • price_analyze: exactly one call, after scraping.
  • send_email: exactly one call, only after analysis.
  • Do not answer the user yourself; rely on tool calls.
""".strip()

        return AssistantAgent(
            name="planner",
            system_message=system_message,
            llm_config=llm_config,
            max_consecutive_auto_reply=6,
            is_termination_msg=lambda x: "TERMINATE" in x.get("content", "").upper(),
        )

    @staticmethod
    def wrap_planner_output(result: Any) -> PlannerAppResponse:
        return PlannerMapper.map_response(result)

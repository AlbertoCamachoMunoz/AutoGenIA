# Archivo: application/dependency_injection.py
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from autogen import GroupChat, GroupChatManager
from autogen.agentchat import AssistantAgent, UserProxyAgent, register_function

from application.dtos.agent_app_request import AgentAppRequest
from application.enums.llm_provider import LLMProvider
from application.interfaces.llm_interface import LLMInterface
from application.factories.llm_provider_factory import LLMProviderFactory

from infrastructure.agents.price_analyzer.price_analyzer_agent import PriceAnalyzerAgent
from infrastructure.agents.webscraper.webscraper_agent import WebScraperAgent
from infrastructure.llms_providers.llm_studio.llm_studio import LLMStudio
from infrastructure.llms_providers.gemini.gemini import Gemini

from infrastructure.autogen_agents.planner_agent import PlannerAgentFactory
from infrastructure.autogen_adapters.agent_autogen_wrapper import AgentAutoGenWrapper
from infrastructure.agents.wikipedia.wikipedia_agent import WikipediaAgent
from infrastructure.agents.email.email_agent import EmailAgent

logger = logging.getLogger(__name__)


class DependencyInjector:
    """
    Inyector de dependencias:
      • Cachea proveedores LLM.
      • Crea y cachea un único set de wrappers (Wikipedia, Email).
      • Construye planner y GroupChatManager con coherencia de instancias.
    """

    # ────────── CACHÉS ──────────
    _provider_cache: Dict[LLMProvider, LLMInterface] = {}
    _wrapper_cache: Optional[List[AgentAutoGenWrapper]] = None

    # ─────── HELPERS LLM PROVIDER ───────
    @staticmethod
    def _llm_studio() -> LLMInterface:
        return LLMStudio()

    @staticmethod
    def _gemini() -> LLMInterface:
        return Gemini()

    @staticmethod
    def get_llm_provider(llm_type: LLMProvider) -> LLMInterface:
        if llm_type not in DependencyInjector._provider_cache:
            provider = LLMProviderFactory(
                llm_studio_provider=DependencyInjector._llm_studio(),
                gemini_provider=DependencyInjector._gemini(),
            ).get_provider(llm_type)
            DependencyInjector._provider_cache[llm_type] = provider
            logger.info("Proveedor LLM «%s» inicializado.", llm_type.value)
        return DependencyInjector._provider_cache[llm_type]

    # ─────── USER PROXY ───────
    @staticmethod
    def _user_agent() -> UserProxyAgent:
        return UserProxyAgent(
            name="usuario",
            human_input_mode="ALWAYS",
            code_execution_config={"use_docker": False},
        )

    # ─────── WRAPPERS (cache única) ───────
    @staticmethod
    def _build_wrappers() -> List[AgentAutoGenWrapper]:
        if DependencyInjector._wrapper_cache is None:
            DependencyInjector._wrapper_cache = [
                # AgentAutoGenWrapper("wikipedia", WikipediaAgent, WikipediaAgent()),
                AgentAutoGenWrapper("scraper", WebScraperAgent, WebScraperAgent()),
                AgentAutoGenWrapper("price_analyze", PriceAnalyzerAgent, PriceAnalyzerAgent()),
                AgentAutoGenWrapper("email",     EmailAgent,     EmailAgent()),
            ]
        return DependencyInjector._wrapper_cache

    # ─────── PLANNER ───────
    @staticmethod
    def _planner_agent(llm_type: LLMProvider) -> AssistantAgent:
        provider   = DependencyInjector.get_llm_provider(llm_type)
        wrappers   = DependencyInjector._build_wrappers() 
        function_list = [fn for w in wrappers for fn in w.get_function_list()]
        return PlannerAgentFactory.create(provider, function_list)

    # ─────── GROUP CHAT MANAGER ───────
    @staticmethod
    def _group_chat_manager(llm_type: LLMProvider) -> GroupChatManager:
        provider = DependencyInjector.get_llm_provider(llm_type)
        planner  = DependencyInjector._planner_agent(llm_type)
        wrappers = DependencyInjector._build_wrappers()   

        llm_cfg = {
            "config_list": [{
                "model":    provider.get_model_name(),
                "base_url": provider.get_base_url(),
                "api_key":  provider.get_api_key(),
            }]
        }

        # Registrar funciones exactamente con esas instancias
        for wrapper in wrappers:
            agent_cls = wrapper.get_agent().__class__

            def _executor(w: AgentAutoGenWrapper):
                def exec_fn(**kwargs: Any) -> Dict[str, str]:
                    dto  = AgentAppRequest(content=kwargs)
                    resp = w.run(dto)
                    return {
                        "content": resp.content,
                        "status":  resp.status.name,
                        "message": resp.message,
                    }
                return exec_fn

            register_function(
                _executor(wrapper),
                name        = agent_cls.get_function_name(),
                description = agent_cls.get_function_description(),
                caller      = planner,
                executor    = wrapper,
            )

        gchat = GroupChat(
            agents  = [planner] + wrappers,
            messages=[],
            max_round=20,
            speaker_selection_method="round_robin",
            allow_repeat_speaker=False,
            select_speaker_auto_llm_config=llm_cfg,
        )
        return GroupChatManager(groupchat=gchat, llm_config=llm_cfg)

    # ─────── PUBLIC API ───────
    @staticmethod
    def get_autogen_user_and_manager(llm_type: LLMProvider) -> Dict[str, Any]:
        """
        Devuelve:
          • 'user'    → UserProxyAgent
          • 'manager' → GroupChatManager
        """
        return {
            "user":    DependencyInjector._user_agent(),
            "manager": DependencyInjector._group_chat_manager(llm_type),
        }

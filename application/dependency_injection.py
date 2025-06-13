from typing import Any, Dict

from autogen import GroupChat, GroupChatManager
from autogen.agentchat import UserProxyAgent, register_function, AssistantAgent

from application.enums.llm_provider import LLMProvider
from application.interfaces.llm_interface import LLMInterface
from application.dtos.agent_app_request import AgentAppRequest

from infrastructure.autogen_agents.planner_agent import PlannerAgentFactory
from infrastructure.autogen_adapters.agent_autogen_wrapper import AgentAutoGenWrapper

from infrastructure.agents.wikipedia.wikipedia_agent import WikipediaAgent
from infrastructure.agents.email.email_agent import EmailAgent  # Simulado

from application.factories.llm_provider_factory import LLMProviderFactory
from infrastructure.llms_providers.gemini.gemini import Gemini
from infrastructure.llms_providers.llm_studio.llm_studio import LLMStudio


class DependencyInjector:
    """
    Inyector de dependencias centrado exclusivamente en los agentes AutoGen.
    """
    # === LLM PROVIDERS ===
    @staticmethod
    def get_llm_provider(llm_type: LLMProvider) -> LLMInterface:
        return LLMProviderFactory(
            llm_studio_provider=DependencyInjector._get_llm_studio_provider(),
            gemini_provider=DependencyInjector._get_gemini_provider()
        ).get_provider(llm_type)

    @staticmethod
    def _get_llm_studio_provider() -> LLMInterface:
        return LLMStudio()

    @staticmethod
    def _get_gemini_provider() -> LLMInterface:
        return Gemini()

    # === AGENTS ===
    @staticmethod
    def get_user_agent() -> UserProxyAgent:
        return UserProxyAgent(name="usuario", human_input_mode="ALWAYS", code_execution_config={"use_docker": False})

    @staticmethod
    def get_wikipedia_agent() -> AgentAutoGenWrapper:
        return AgentAutoGenWrapper(name="wikipedia", agent_class=WikipediaAgent, agent=WikipediaAgent())

    @staticmethod
    def get_email_agent() -> AgentAutoGenWrapper:
        return AgentAutoGenWrapper(name="email", agent_class=EmailAgent, agent=EmailAgent())

    @staticmethod
    def get_planner_agent(llm_type: LLMProvider) -> AssistantAgent:
        provider = DependencyInjector.get_llm_provider(llm_type)

        functional_wrappers = [
            DependencyInjector.get_email_agent(),
        ]

        function_list = []
        for wrapper in functional_wrappers:
            try:
                functions = wrapper.get_function_list()
                function_list.extend(functions)
            except NotImplementedError:
                continue

        return PlannerAgentFactory.create(provider, function_list)

    # === BUILD group chat ===
    @staticmethod
    def get_autogen_groupchat(llm_type: LLMProvider) -> GroupChatManager:
        provider: LLMInterface = DependencyInjector.get_llm_provider(llm_type)
        planner = DependencyInjector.get_planner_agent(llm_type)

        functional_wrappers = [
            DependencyInjector.get_wikipedia_agent(),
            DependencyInjector.get_email_agent()
        ]

        llm_config_for_selection = {
            "config_list": [{
                "model": provider.get_model_name(),
                "base_url": provider.get_base_url(),
                "api_key": provider.get_api_key()
            }]
        }

        # Función que crea una función ejecutable por AutoGen
        def create_function_executor(wrapper: AgentAutoGenWrapper):
            def function_executor(**kwargs: Any) -> Dict[str, str]:
                response = wrapper.run(AgentAppRequest(content=kwargs))
                return {
                    "content": response.content,
                    "status": response.status.name,
                    "message": response.message
                }
            return function_executor

        # Registrar todas las funciones dinámicamente
        for wrapper in functional_wrappers:
            agent_class = wrapper._agent.__class__
            function_name = agent_class.get_function_name()
            function_desc = agent_class.get_function_description()

            executor_func = create_function_executor(wrapper)

            register_function(
                executor_func,
                name=function_name,
                description=function_desc,
                caller=planner,
                executor=wrapper
            )

        groupchat = GroupChat(
            agents=[planner] + functional_wrappers,
            messages=[],
            max_round=10,
            speaker_selection_method="auto",
            allow_repeat_speaker=False,
            select_speaker_auto_llm_config=llm_config_for_selection
        )

        return GroupChatManager(groupchat=groupchat, llm_config=llm_config_for_selection)

    @staticmethod
    def get_autogen_user_and_manager(llm_type: LLMProvider) -> dict:
        user = DependencyInjector.get_user_agent()
        manager = DependencyInjector.get_autogen_groupchat(llm_type)
        return {"user": user, "manager": manager}

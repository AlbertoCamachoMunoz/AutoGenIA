from autogen import GroupChat, GroupChatManager
from autogen.agentchat import UserProxyAgent, register_function

from application.enums.llm_provider import LLMProvider
from application.interfaces.llm_interface import LLMInterface
from application.interfaces.agent_interface import AgentInterface

from infrastructure.autogen_agents.planner_agent import create_planner_agent
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

    # === Agentes funcionales ===

    @staticmethod
    def get_user_agent() -> UserProxyAgent:
        return UserProxyAgent(name="usuario", human_input_mode="ALWAYS", code_execution_config={"use_docker": False})

    @staticmethod
    def get_wikipedia_agent() -> AgentInterface:
        return WikipediaAgent()

    @staticmethod
    def get_email_agent() -> AgentInterface:
        return EmailAgent()

    @staticmethod
    def get_planner_agent(llm_type: LLMProvider) -> AgentInterface:
        provider = DependencyInjector.get_llm_provider(llm_type)
        return create_planner_agent(provider)

    @staticmethod
    def get_autogen_groupchat(llm_type: str) -> GroupChatManager:
        provider: LLMInterface = DependencyInjector.get_llm_provider(llm_type)

        planner = create_planner_agent(provider)
        wikipedia = AgentAutoGenWrapper(name="wikipedia", agent=DependencyInjector.get_wikipedia_agent())

        # ---- registrar las funciones de los ejecutores en el planner ----
        def execute_wikipedia(title: str) -> str:
            """
            Busca información en Wikipedia a partir de un título.

            Args:
                title (str): Título del artículo de Wikipedia
            
            Returns:
                str: Contenido limpio del artículo
            """
            return DependencyInjector.get_wikipedia_agent().run(title)

        register_function(
            execute_wikipedia,
            name="wikipedia",
            description="Busca información en Wikipedia a partir de un título.",
            caller=planner,
            executor=wikipedia
        )

        llm_config_for_selection = {
            "config_list": [{
                "model": provider.get_model_name(),
                "base_url": provider.get_base_url(),
                "api_key": provider.get_api_key()
            }]
        }

        groupchat = GroupChat(
            agents=[planner, wikipedia],
            messages=[],
            max_round=5,
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
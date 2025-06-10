from autogen.agentchat import UserProxyAgent
from autogen import GroupChat, GroupChatManager

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

    # === LLMs disponibles ===

    @staticmethod
    def get_llm_provider(llm_type: LLMProvider) -> LLMInterface:
        """
        Devuelve la implementación del proveedor de LLM elegido.

        Args:
            llm_type (LLMProvider): Enumeración del proveedor deseado.

        Returns:
            LLMInterface: Proveedor LLM concreto.
        """
        return LLMProviderFactory(
            llm_studio=DependencyInjector._get_llm_studio_provider(),
            gemini=DependencyInjector._get_gemini_provider()
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
        return UserProxyAgent(name="usuario", human_input_mode="ALWAYS")

    @staticmethod
    def get_wikipedia_agent() -> AgentInterface:
        return WikipediaAgent()

    @staticmethod
    def get_email_agent() -> AgentInterface:
        return EmailAgent()

    @staticmethod
    def get_planner_agent(llm_type: LLMProvider) -> AgentInterface:
        """
        Devuelve el agente planificador con el LLM que el usuario ha indicado.

        Args:
            llm_type (LLMProvider): Tipo de LLM deseado para el planner.

        Returns:
            AssistantAgent: Planner configurado.
        """
        provider = DependencyInjector.get_llm_provider(llm_type)
        return create_planner_agent(provider)

    # === Entorno AutoGen ===

    @staticmethod
    def get_autogen_groupchat(llm_type: LLMProvider) -> GroupChatManager:
        """
        Construye y devuelve el GroupChatManager con los agentes funcionales y el planner.

        Args:
            llm_type (LLMProvider): LLM elegido para el planner.

        Returns:
            GroupChatManager: Orquestador del grupo AutoGen.
        """
        user = DependencyInjector.get_user_agent()
        planner = DependencyInjector.get_planner_agent(llm_type)
        wikipedia = AgentAutoGenWrapper(name="wikipedia", agent=DependencyInjector.get_wikipedia_agent())
        email = AgentAutoGenWrapper(name="email", agent=DependencyInjector.get_email_agent())

        group = GroupChat(
            agents=[user, planner, wikipedia, email],
            messages=[]
        )

        return GroupChatManager(groupchat=group)

    @staticmethod
    def get_autogen_user_and_manager(llm_type: LLMProvider) -> dict:
        """
        Inyecta los objetos necesarios al caso de uso.

        Args:
            llm_type (LLMProvider): LLM elegido para el planner.

        Returns:
            dict: {'user': UserProxyAgent, 'manager': GroupChatManager}
        """
        user = DependencyInjector.get_user_agent()
        manager = DependencyInjector.get_autogen_groupchat(llm_type)
        return {
            "user": user,
            "manager": manager
        }

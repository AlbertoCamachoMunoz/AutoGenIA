from autogen import GroupChat, GroupChatManager
from autogen.agentchat import UserProxyAgent, register_function, AssistantAgent

from application.enums.llm_provider import LLMProvider
from application.interfaces.llm_interface import LLMInterface
from application.interfaces.agent_interface import AgentInterface
from application.dtos.agent_app_request import AgentAppRequest


from infrastructure.autogen_agents.planner_agent import create_planner_agent
from infrastructure.autogen_adapters.agent_autogen_wrapper import AgentAutoGenWrapper

from infrastructure.agents.wikipedia.wikipedia_agent import WikipediaAgent
from infrastructure.agents.email.email_agent import EmailAgent  # Simulado

from application.factories.llm_provider_factory import LLMProviderFactory
from infrastructure.llms_providers.gemini.gemini import Gemini
from infrastructure.llms_providers.llm_studio.llm_studio import LLMStudio


# Definición del function_list
FUNCTION_LIST = [
    {
        "name": "wikipedia_search",
        "description": "Busca contenido limpio de Wikipedia.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Título del artículo de Wikipedia"}
            },
            "required": ["title"]
        }
    }
]


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
        return UserProxyAgent(
            name="usuario",
            human_input_mode="ALWAYS",
            code_execution_config={"use_docker": False}
        )

    @staticmethod
    def get_wikipedia_agent() -> AgentAutoGenWrapper:
        return AgentAutoGenWrapper(name="wikipedia", agent=WikipediaAgent())

    @staticmethod
    def get_email_agent() -> AgentAutoGenWrapper:
        return AgentAutoGenWrapper(name="email", agent=EmailAgent())

    @staticmethod
    def get_planner_agent(llm_type: LLMProvider) -> AssistantAgent:
        provider = DependencyInjector.get_llm_provider(llm_type)
        return create_planner_agent(provider, functions=FUNCTION_LIST)

    @staticmethod
    def get_autogen_groupchat(llm_type: LLMProvider) -> GroupChatManager:
        provider: LLMInterface = DependencyInjector.get_llm_provider(llm_type)

        # Crear planner con funciones inyectadas
        planner = DependencyInjector.get_planner_agent(llm_type)
        wikipedia = DependencyInjector.get_wikipedia_agent()

        # Función real que se ejecutará cuando se llame desde el planner
        def execute_wikipedia(title: str) -> dict:
            response = WikipediaAgent().run(AgentAppRequest(input_data=title))
            return {
                "content": response.content,
                "status": response.status.name,  # Pasamos el nombre del enum como string
                "message": response.message
            }

        # Registrar la función en AutoGen
        register_function(
            execute_wikipedia,
            name="wikipedia_search",  # Nombre debe coincidir con FUNCTION_LIST
            description="Busca contenido limpio de Wikipedia.",
            caller=planner,   # Quién puede invocar esta función
            executor=wikipedia  # Quién la ejecuta
        )

        # Configuración para seleccionar speakers
        llm_config_for_selection = {
            "config_list": [{
                "model": provider.get_model_name(),
                "base_url": provider.get_base_url(),
                "api_key": provider.get_api_key()
            }]
        }

        # Grupo de chat
        groupchat = GroupChat(
            agents=[planner, wikipedia],
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
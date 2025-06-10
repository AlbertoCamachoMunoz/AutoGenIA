from autogen.agentchat import UserProxyAgent
from autogen.agentchat.groupchat import GroupChatManager


def run_autogen_chat(
    user: UserProxyAgent,
    manager: GroupChatManager,
    user_prompt: str
) -> None:
    """
    Caso de uso: ejecuta la conversación AutoGen.

    Args:
        user (UserProxyAgent): Usuario humano (inyectado).
        manager (GroupChatManager): Orquestador del grupo (inyectado).
        user_prompt (str): Mensaje inicial que lanza el flujo.
    """
    user.initiate_chat(
        manager,
        message=user_prompt
    )
from autogen.agentchat import UserProxyAgent, GroupChat

from infrastructure.autogen_agents.shared_buffer import get_last_json  # type: ignore


def run_autogen_chat(user: UserProxyAgent, manager: GroupChat, user_prompt: str):
    """
    Lanza la conversación Autogen y devuelve el ChatResult original.
    """
    print("-------------- Antes -------------------------")
    user.initiate_chat(manager, message=user_prompt)
    print(get_last_json())
    return get_last_json()
    print("-------------- Después ------------------------")
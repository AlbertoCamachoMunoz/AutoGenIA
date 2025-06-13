from autogen.agentchat import UserProxyAgent, GroupChat  # type: ignore


def run_autogen_chat(user: UserProxyAgent, manager: GroupChat, user_prompt: str):
    """
    Lanza la conversación Autogen y devuelve el ChatResult original.
    """
    return user.initiate_chat(manager, message=user_prompt)

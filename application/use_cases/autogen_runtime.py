from buffer.shared_buffer import get_last_json 
from autogen.agentchat import UserProxyAgent, GroupChat


def run_autogen_chat(user: UserProxyAgent, manager: GroupChat, user_prompt: str):
    """
    Lanza la conversación Autogen y devuelve el ChatResult original.
    """
    user.initiate_chat(manager, message=user_prompt)
    return  get_last_json()  # Devolvemos el último JSON del buffer compartido

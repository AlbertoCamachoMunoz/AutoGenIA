# infrastructure/autogen_agents/shared_buffer.py

import threading

# Buffer thread-safe para almacenar el último JSON de resultado
_last_json_lock = threading.Lock()
_last_json = None

def set_last_json(json_result):
    """
    Guarda el último JSON resultado.
    """
    global _last_json
    with _last_json_lock:
        _last_json = json_result

def get_last_json():
    """
    Recupera el último JSON resultado.
    """
    with _last_json_lock:
        return _last_json
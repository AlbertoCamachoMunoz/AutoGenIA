import os

# Configuración para LLM Studio
LLM_STUDIO_API_URL = os.getenv("LLM_STUDIO_API_URL", "")
LLM_STUDIO_API_KEY = os.getenv("LLM_STUDIO_API_KEY", "")
LLM_STUDIO_DEFAULT_NAME = os.getenv("LLM_STUDIO_DEFAULT_NAME", "llm-studio")
LLM_STUDIO_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {LLM_STUDIO_API_KEY}"
}

# Configuración para Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Obtiene la ruta base del proyecto (un nivel por encima de la carpeta config)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ruta para los ficheros de audio generados
AUDIO_OUTPUT_FOLDER = os.path.join(BASE_DIR, "presentation", "front_app", "generated_audio")

# Ruta para los ficheros de audio que sube el usuario (entrada)
AUDIO_INPUT_FOLDER = os.path.join(BASE_DIR, "presentation", "front_app", "temp_uploads")

# Asegurar que existan las carpetas
os.makedirs(AUDIO_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(AUDIO_INPUT_FOLDER, exist_ok=True)

# RUTA COMPLETA para el fichero de salida TTS, si deseas un nombre fijo
AUDIO_OUTPUT_FILE = os.path.join(AUDIO_OUTPUT_FOLDER, "output.wav")

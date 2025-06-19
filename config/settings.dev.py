import os

# Configuración para LLM Studio
LLM_STUDIO_API_URL = os.getenv("LLM_STUDIO_API_URL", "http://localhost:1234/v1")
LLM_STUDIO_API_KEY = os.getenv("LLM_STUDIO_API_KEY", "MI_TOKEN")
LLM_STUDIO_DEFAULT_NAME = os.getenv("LLM_STUDIO_DEFAULT_NAME", "Hermes-2-Pro-Llama-3-8B")
# LLM_STUDIO_DEFAULT_NAME = os.getenv("LLM_STUDIO_DEFAULT_NAME", "Hermes-3-Llama-3.1-8B")
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

# Configuración para el servicio SMTP
SMTP_SERVER = os.getenv("SMTP_SERVER", "sandbox.smtp.mailtrap.io")
SMTP_PORT = int(os.getenv("SMTP_PORT", "2525"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "0b8912a4ed76be")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "226639342b6cff")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "AutoGenIA <autogenia@example.com>")


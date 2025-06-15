# presentation/cli_app.py
"""
CLI interactiva para AutoGen IA – versión iterativa y robusta.
"""

import logging
import sys
from requests.exceptions import ConnectionError
from openai import NotFoundError, OpenAIError

# Configuración del logging
logging.basicConfig(level=logging.ERROR, format="%(message)s")
logging.getLogger("autogen.oai.client").setLevel(logging.CRITICAL)

# Importaciones locales
from application.use_cases.autogen_runtime import run_autogen_chat
from application.dependency_injection import DependencyInjector
from application.enums.llm_provider import LLMProvider
from utils.planner_helpers import last_planner_response


def main() -> None:
    print("=== AUTO-GEN CLI ===")
    print("Selecciona el modelo LLM:")
    print("1. Gemini")
    print("2. LLM Studio")
    opcion = input("Opción (1/2): ").strip()

    if opcion == "1":
        llm_type = LLMProvider.GEMINI
    elif opcion == "2":
        llm_type = LLMProvider.LLM_STUDIO
    else:
        print("Opción no válida.")
        return

    deps = DependencyInjector.get_autogen_user_and_manager(llm_type)
    user = deps["user"]
    manager = deps["manager"]

    print("\nEscribe tu mensaje (exit para salir)\n")

    while True:
        prompt = input("> ").strip()
        if prompt.lower() in ("exit", "salir", "quit"):
            break
        if not prompt:
            continue

        try:
            # Limpiar historial previo si es necesario
            manager.groupchat.messages = []

            # Ejecutar conversación
            run_autogen_chat(user, manager, prompt)

            # Mostrar respuesta del planner siempre como DTO coherente
            planner_dto = last_planner_response(manager.groupchat.messages)

            print("\n--- Planner ----------------------------------------")
            print(planner_dto.content)
            print(f"[{planner_dto.message}]")
            print("----------------------------------------------------\n")

        except ConnectionError:
            print(
                "\n🚫 No se pudo conectar con LM Studio.\n"
                "Revisa la URL y si el servidor está encendido.\n"
            )
        except NotFoundError:
            print(
                "\n⚠️ El modelo no está cargado en LM Studio.\n"
                "Carga un modelo o revisa la configuración.\n"
            )
        except OpenAIError as e:
            print(f"\n⚠️ Error OpenAI-compatible: {e}\n")
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")
        sys.exit(0)

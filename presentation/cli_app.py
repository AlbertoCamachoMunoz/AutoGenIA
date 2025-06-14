"""
CLI interactiva para AutoGen IA.

• Permite elegir proveedor (Gemini o LLM Studio).
• Mantiene la misma sesión de usuario y GroupChatManager entre mensajes.
• Captura los errores más habituales de LLM Studio y muestra mensajes claros.
"""

import logging
import sys
from requests.exceptions import ConnectionError
from openai import NotFoundError, OpenAIError   # ← corrección de import

# Reducimos ruido de Autogen
logging.basicConfig(level=logging.ERROR, format="%(message)s")

from application.use_cases.autogen_runtime import run_autogen_chat
from application.dependency_injection import DependencyInjector
from application.enums.llm_provider import LLMProvider


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

    # Crea agentes y orquestador solo una vez
    deps = DependencyInjector.get_autogen_user_and_manager(llm_type)
    user = deps["user"]
    manager = deps["manager"]

    print("\nEscribe tu mensaje ( exit para salir )\n")

    while True:
        prompt = input("> ").strip()
        if prompt.lower() in ("exit", "salir", "quit"):
            break
        if not prompt:
            continue

        try:
            # Ejecuta / continúa la conversación
            run_autogen_chat(user, manager, prompt)

            # Última respuesta del planner
            last_planner_msg = next(
                (m for m in reversed(manager.groupchat.messages) if m.get("role") == "planner"),
                {"content": "[sin respuesta]"},
            )
            print("\n🧠 Planner:\n" + last_planner_msg["content"] + "\n")

        # ─────── manejo de errores amable ─────────
        except NotFoundError:
            print(
                "\n⚠️  El modelo solicitado no está cargado en LLM Studio.\n"
                "   Abre LLM Studio, pulsa ▶ Run sobre el modelo o elige otro,\n"
                "   y vuelve a intentarlo.\n"
            )

        except ConnectionError:
            print(
                "\n⚠️  No se pudo conectar con LLM Studio en http://localhost:1234/v1.\n"
                "   Asegúrate de que el servidor está en ejecución.\n"
            )

        except OpenAIError as e:
            print(f"\n⚠️  Error OpenAI-compatible: {e}\n")

        except Exception as e:
            print(f"\n❌  Error inesperado: {e}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido por el usuario.")
        sys.exit(0)

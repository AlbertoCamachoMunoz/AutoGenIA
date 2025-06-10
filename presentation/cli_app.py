# cli.py

from application.use_cases.autogen_runtime import run_autogen_chat
from infrastructure.dependency_injector import DependencyInjector
from application.enums.llm_provider import LLMProvider


def main():
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

    prompt = input("\nEscribe tu mensaje (ej: Busca info sobre Einstein y mándamela por email a x@x.com):\n> ")

    deps = DependencyInjector.get_autogen_user_and_manager(llm_type)

    run_autogen_chat(
        user=deps["user"],
        manager=deps["manager"],
        user_prompt=prompt
    )


if __name__ == "__main__":
    main()

# cli.py
import logging
logging.basicConfig(level=logging.ERROR, format="%(message)s")  # nivel global

from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

try:
    from flask_cors import CORS
except ModuleNotFoundError:  # la librería es opcional si sólo se usa CLI
    def CORS(_app):  # type: ignore
        ...
# ──────────────────────────────────────────
from application.enums.llm_provider import LLMProvider
from application.dependency_injection import DependencyInjector
from application.use_cases.autogen_runtime import run_autogen_chat


# ── flask ───────────────────────────────────────────────
app = Flask(__name__, static_folder="./front_app", static_url_path="")
CORS(app)


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/chat", methods=["POST"])
def chat():
    body = request.get_json(force=True) or {}
    prompt = (body.get("prompt") or "").strip()
    llm_type = LLMProvider(body.get("llm_type", "llm_studio"))

    if not prompt:
        return jsonify(status="error", message="El campo 'prompt' no puede estar vacío."), 400

    try:
        deps = DependencyInjector.get_autogen_user_and_manager(llm_type)
        chat_result = run_autogen_chat(deps["user"], deps["manager"], prompt)

        history = getattr(chat_result, "messages", []) or getattr(chat_result, "chat_history", [])
        planner_reply = next((m for m in reversed(history) if m.get("role") == "planner"), {})

        return jsonify(
            status="success",
            llm_type=llm_type.value,
            result=planner_reply.get("content", ""),
            trace=history,
        ), 200

    except Exception as exc:  # pragma: no cover
        return jsonify(status="error", message="Internal server error", detail=str(exc)), 500


if __name__ == "__main__":
    HOST, PORT = "127.0.0.1", 5000
    banner = "\n" + "━" * 66 + f"\n  🚀  ChatIA running at:  http://{HOST}:{PORT}\n" + "━" * 66 + "\n"
    print(banner, flush=True)
    app.run(debug=True, host=HOST, port=PORT)

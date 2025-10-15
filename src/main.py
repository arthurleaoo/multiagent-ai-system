"""
Ponto de entrada principal do sistema multi-agente.
"""
import os
import logging
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

from src.config.config import Config
from src.core.genai_client import GenAIClient
from src.core.mcp_handler import MCPHandler
from src.agents.front_agent import FrontAgent
from src.agents.back_agent import BackAgent
from src.agents.qa_agent import QAAgent
from src.agents.orchestrator import Orchestrator

# --- Carregar variáveis de ambiente da raiz do projeto ---
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# --- Configurar logging ---
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Inicializar o aplicativo Flask ---
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "chave_secreta_padrao")
app.config["DEBUG"] = os.getenv("DEBUG", "False").lower() == "true"

# --- Carregar configurações ---
config = Config()
if os.getenv("OPENAI_API_KEY"):
    config.set_openai_api_key(os.getenv("OPENAI_API_KEY"))

# --- Inicializar o cliente GenAI ---
genai_client = GenAIClient(
    api_key=config.get_openai_api_key(),
    model=config.get_model()
)

# --- Inicializar o handler MCP ---
mcp_handler = MCPHandler()

# --- Inicializar os agentes ---
front_agent = FrontAgent(genai_client=genai_client, mcp_handler=mcp_handler)
back_agent = BackAgent(genai_client=genai_client, mcp_handler=mcp_handler)
qa_agent = QAAgent(genai_client=genai_client, mcp_handler=mcp_handler)

# --- Inicializar o orquestrador ---
orchestrator = Orchestrator(
    front_agent=front_agent,
    back_agent=back_agent,
    qa_agent=qa_agent
)

# ----- Rotas padrão -----
@app.route("/")
def index():
    return render_template("index.html")

# ----- API Routes -----
@app.route("/api/process", methods=["POST"])
def process_task():
    """
    Processa uma tarefa enviada via API.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "Dados não fornecidos"}), 400
            
        # Verificar tipo de tarefa
        task_type = data.get("type", "process")
        
        if task_type == "generate_code":
            result = orchestrator.generate_code(data)
        else:
            result = orchestrator.process_task(data)
            
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erro ao processar tarefa: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Erro ao processar tarefa: {str(e)}"
        }), 500
if __name__ == "__main__":
    # Verificar se a chave da API está configurada
    if not config.get_openai_api_key():
        logger.error("Chave da API OpenAI não configurada. Configure em config.json ou defina OPENAI_API_KEY no ambiente.")
        exit(1)
        
    # Iniciar o servidor Flask
    app.run(host="0.0.0.0", port=5000)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout realizado com sucesso!", "success")
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/task/new", methods=["GET", "POST"])
@login_required
def new_task():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        result = orchestrator.process_task({
            "title": title,
            "description": description,
            "user_id": current_user.id
        })
        flash("Tarefa criada e enviada para processamento!", "success")
        return redirect(url_for("dashboard"))
    return render_template("new_task.html")

# ----- Rota de teste API para Postman/Insomnia -----
@app.route("/api/agent/message", methods=["POST"])
# @login_required  ## opcional: remova se quiser testar sem login
def api_agent_message():
    data = request.get_json()
    if not data or "agent_type" not in data or "content" not in data:
        return jsonify({"error": "Payload inválido"}), 400

    agent_type = data["agent_type"].lower()
    content = data["content"]

    agent_map = {
        "front": front_agent,
        "back": back_agent,
        "qa": qa_agent
    }

    agent = agent_map.get(agent_type)
    if not agent:
        return jsonify({"error": "Tipo de agente inválido"}), 400

    try:
        response = agent.process_message({"role": "user", "content": content})
        return jsonify(response)
    except Exception as e:
        logger.exception("Erro ao processar mensagem")
        return jsonify({"error": str(e)}), 500

# ----- Rodar Flask -----
if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 5000))
    app.run(host=host, port=port)

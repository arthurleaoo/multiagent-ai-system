"""
Ponto de entrada principal do sistema multi-agente (versão pronta para testes via API).
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from src.data.database import init_db, get_db, User
from src.orchestrator.orchestrator import Orchestrator
from src.core.genai_client import GenAIClient
from src.auth.auth_manager import AuthManager
from src.agents.front_agent import FrontAgent
from src.agents.back_agent import BackAgent
from src.agents.qa_agent import QAAgent

# --- Carregar variáveis de ambiente da raiz do projeto ---
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Verificação opcional
print("OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))

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

# --- Configurar o gerenciador de login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# --- Inicializar o banco de dados ---
init_db()

# --- Inicializar o cliente GenAI ---
genai_client = GenAIClient(
    api_key=os.getenv("OPENAI_API_KEY")  # ⚡ chave segura
)

# --- Inicializar os agentes ---
front_agent = FrontAgent(genai_client=genai_client)
back_agent = BackAgent(genai_client=genai_client)
qa_agent = QAAgent(genai_client=genai_client)


# --- Inicializar o orquestrador ---
orchestrator = Orchestrator(
    front_agent=front_agent,
    back_agent=back_agent,
    qa_agent=qa_agent,
    db=get_db(),
    logger=logger
)

# ----- Flask Login -----
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))

# ----- Rotas padrão -----
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        db = get_db()
        user = db.query(User).filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Credenciais inválidas. Tente novamente.", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        db = get_db()
        existing_user = db.query(User).filter_by(username=username).first()
        if existing_user:
            flash("Nome de usuário já existe. Escolha outro.", "danger")
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.add(new_user)
            db.commit()
            flash("Registro realizado com sucesso! Faça login.", "success")
            return redirect(url_for("login"))
    return render_template("register.html")

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

"""
Módulo para persistência de dados do sistema (SQLite).
Inclui a classe User para Flask-Login e helpers para tasks e interações.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import logging
from typing import Optional, Dict, Any
from flask_login import UserMixin

logger = logging.getLogger("database")

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data.db")

# --- Classe User compatível Flask-Login ---
class User(UserMixin):
    """Classe wrapper para usuários (Flask-Login)."""
    def __init__(self, id: int, username: str, email: str, password_hash: str):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_id(user_id: int) -> Optional["User"]:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return User(row["id"], row["username"], row["email"], row["password_hash"])

    @staticmethod
    def get_by_username(username: str) -> Optional["User"]:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return User(row["id"], row["username"], row["email"], row["password_hash"])


# --- Inicialização do DB ---
def init_db() -> None:
    """Inicializa o banco de dados criando todas as tabelas necessárias."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT,
        description TEXT,
        status TEXT DEFAULT 'em_andamento',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS agents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role TEXT,
        ai_provider TEXT,
        system_prompt TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        agent_id INTEGER,
        title TEXT NOT NULL,
        input_usuario TEXT,
        output_gerado TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        user_id INTEGER,
        FOREIGN KEY (project_id) REFERENCES projects (id),
        FOREIGN KEY (agent_id) REFERENCES agents (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS agent_interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        agent_name TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES tasks (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ia_interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        messages TEXT,
        tokens_usados INTEGER,
        custo_estimo DECIMAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES tasks (id)
    )
    ''')

    conn.commit()
    conn.close()
    logger.debug("Banco inicializado em %s", DB_PATH)


# --- Conexão helper ---
def get_db() -> sqlite3.Connection:
    """Retorna uma conexão sqlite3 (lembre-se de fechar depois)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# --- Helpers para tarefas e interações ---
def create_task(title: str, description: str, user_id: int, project_id: Optional[int] = None, agent_id: Optional[int] = None) -> int:
    """Insere uma tarefa e retorna o id gerado."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (project_id, agent_id, title, input_usuario, status, user_id) VALUES (?, ?, ?, ?, ?, ?)",
        (project_id, agent_id, title, description, "processing", user_id)
    )
    task_id = cur.lastrowid
    conn.commit()
    conn.close()
    logger.debug("Task criada id=%s title=%s", task_id, title)
    return task_id


def get_task(task_id: int) -> Optional[Dict[str, Any]]:
    """Retorna um dicionário com os dados da tarefa ou None."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def update_task_status(task_id: int, status: str, output_gerado: Optional[str] = None) -> None:
    """Atualiza status e opcionalmente output_gerado/completed_at."""
    conn = get_db()
    cur = conn.cursor()
    if output_gerado is not None:
        cur.execute(
            "UPDATE tasks SET status = ?, output_gerado = ?, completed_at = ? WHERE id = ?",
            (status, output_gerado, datetime.utcnow(), task_id)
        )
    else:
        cur.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    conn.commit()
    conn.close()
    logger.debug("Task %s atualizado para status=%s", task_id, status)


def log_interaction(task_id: int, agent_name: str, message: str) -> None:
    """Registra uma interação de agente na tabela agent_interactions."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO agent_interactions (task_id, agent_name, message) VALUES (?, ?, ?)",
        (task_id, agent_name, message)
    )
    conn.commit()
    conn.close()
    logger.debug("Interaction logged for task=%s agent=%s", task_id, agent_name)

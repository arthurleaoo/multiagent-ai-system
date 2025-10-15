import sqlite3
import hashlib
from typing import Optional

DB_PATH = "src/data/database.db"  # Ajuste conforme sua estrutura

class AuthManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Cria a tabela de usuários se não existir."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )
            """)
            conn.commit()

    def _hash_password(self, password: str) -> str:
        """Hash simples usando SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username: str, password: str) -> bool:
        """Registra um novo usuário."""
        password_hash = self._hash_password(password)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, password_hash)
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Usuário já existe
            return False

    def authenticate_user(self, username: str, password: str) -> bool:
        """Verifica se as credenciais estão corretas."""
        password_hash = self._hash_password(password)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE username = ? AND password_hash = ?",
                (username, password_hash)
            )
            result = cursor.fetchone()
            return result is not None

    def get_user_id(self, username: str) -> Optional[int]:
        """Retorna o ID do usuário dado o username."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return row[0] if row else None

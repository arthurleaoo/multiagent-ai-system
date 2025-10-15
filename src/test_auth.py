from src.auth.auth_manager import AuthManager
from src.auth.session import SessionManager

def main():
    auth = AuthManager()
    sessions = SessionManager()

    username = "arthur"
    password = "senha123"

    # 1️⃣ Registrar usuário
    if auth.register_user(username, password):
        print(f"Usuário '{username}' registrado com sucesso!")
    else:
        print(f"Usuário '{username}' já existe.")

    # 2️⃣ Autenticar usuário
    if auth.authenticate_user(username, password):
        user_id = auth.get_user_id(username)
        print(f"Autenticação OK. ID do usuário: {user_id}")

        # 3️⃣ Criar sessão
        session_token = sessions.create_session(user_id)
        print(f"Token da sessão criado: {session_token}")

        # 4️⃣ Recuperar usuário pela sessão
        user_from_session = sessions.get_user(session_token)
        print(f"Usuário recuperado pela sessão: {user_from_session}")

        # 5️⃣ Finalizar sessão
        sessions.destroy_session(session_token)
        print("Sessão encerrada com sucesso.")
    else:
        print("Autenticação falhou. Credenciais inválidas.")

if __name__ == "__main__":
    main()

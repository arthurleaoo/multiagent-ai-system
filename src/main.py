from src.auth.auth_manager import AuthManager
from src.auth.session import SessionManager
from src.orchestrator.orchestrator import Orchestrator
from src.agents.front_agent import FrontAgent
from src.agents.back_agent import BackAgent
from src.agents.qa_agent import QAAgent

def main():
    auth = AuthManager()
    sessions = SessionManager()

    print("=== Multiagente IA System ===")
    username = input("Usuário: ")
    password = input("Senha: ")

    # 1️⃣ Autenticação
    if not auth.authenticate_user(username, password):
        print("Credenciais inválidas. Encerrando sistema.")
        return

    user_id = auth.get_user_id(username)
    session_token = sessions.create_session(user_id)
    print(f"Login bem-sucedido! Sessão criada: {session_token}")

    # 2️⃣ Inicializar agentes
    front_agent = FrontAgent()
    back_agent = BackAgent()
    qa_agent = QAAgent()

    # 3️⃣ Inicializar orquestrador
    orchestrator = Orchestrator(front_agent, back_agent, qa_agent, sessions)

    # 4️⃣ Executar fluxo de tarefas (exemplo)
    # O orquestrador só envia tarefas se a sessão for válida
    task = input("Digite a tarefa para o sistema: ")
    result = orchestrator.run_task(task, session_token)

    print("Resultado da tarefa:", result)

    # 5️⃣ Encerrar sessão
    sessions.destroy_session(session_token)
    print("Sessão encerrada. Sistema finalizado.")

if __name__ == "__main__":
    main()

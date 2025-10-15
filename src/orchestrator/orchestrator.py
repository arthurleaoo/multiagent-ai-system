# src/orchestrator/orchestrator.py
class Orchestrator:
    def __init__(self, front_agent, back_agent, qa_agent, session_manager):
        self.front_agent = front_agent
        self.back_agent = back_agent
        self.qa_agent = qa_agent
        self.sessions = session_manager

    def run_task(self, task: str, session_token: str):
        # Verifica sessão
        user_id = self.sessions.get_user(session_token)
        if not user_id:
            return "Sessão inválida ou expirada."

        # Exemplo simples de delegação de tarefas
        if "front" in task.lower():
            return self.front_agent.execute(task)
        elif "back" in task.lower():
            return self.back_agent.execute(task)
        elif "qa" in task.lower():
            return self.qa_agent.execute(task)
        else:
            return "Tarefa não reconhecida."

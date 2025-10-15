import uuid

class SessionManager:
    def __init__(self):
        self.sessions = {}  # {session_id: user_id}

    def create_session(self, user_id: int) -> str:
        """Cria uma nova sessão e retorna o token."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = user_id
        return session_id

    def get_user(self, session_id: str) -> int | None:
        """Retorna o user_id associado à sessão."""
        return self.sessions.get(session_id)

    def destroy_session(self, session_id: str):
        """Encerra a sessão."""
        if session_id in self.sessions:
            del self.sessions[session_id]

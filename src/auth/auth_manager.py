"""
Gerenciador de autenticação para o sistema multi-agente.
"""
import os
import jwt
import datetime
from typing import Dict, Optional, Tuple
from .session import Session

class AuthManager:
    """
    Gerencia autenticação e autorização de usuários no sistema.
    """
    def __init__(self, secret_key: Optional[str] = None):
        """
        Inicializa o gerenciador de autenticação.
        
        Args:
            secret_key: Chave secreta para assinatura de tokens JWT.
                        Se não fornecida, usa a variável de ambiente JWT_SECRET_KEY.
        """
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY", "default_secret_key_change_in_production")
        self.sessions = {}  # Armazena sessões ativas
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Autentica um usuário com nome de usuário e senha.
        
        Args:
            username: Nome de usuário
            password: Senha
            
        Returns:
            Tupla contendo (sucesso, dados_do_usuário, mensagem_de_erro)
        """
        from src.data.database import get_user_by_username
        
        user = get_user_by_username(username)
        if not user:
            return False, None, "Usuário não encontrado"
        
        # Verificar senha (assumindo que está armazenada com hash)
        if not user.verify_password(password):
            return False, None, "Senha incorreta"
        
        return True, user.to_dict(), None
    
    def create_token(self, user_data: Dict) -> str:
        """
        Cria um token JWT para o usuário autenticado.
        
        Args:
            user_data: Dados do usuário a serem incluídos no token
            
        Returns:
            Token JWT assinado
        """
        payload = {
            'sub': str(user_data['id']),
            'username': user_data['username'],
            'role': user_data.get('role', 'user'),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        
        # Criar sessão para o usuário
        session = Session(user_id=user_data['id'], token=token)
        self.sessions[token] = session
        
        return token
    
    def validate_token(self, token: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Valida um token JWT e retorna os dados do usuário.
        
        Args:
            token: Token JWT a ser validado
            
        Returns:
            Tupla contendo (sucesso, dados_do_usuário, mensagem_de_erro)
        """
        try:
            # Verificar se o token existe nas sessões ativas
            if token not in self.sessions:
                return False, None, "Sessão inválida ou expirada"
            
            # Verificar se a sessão expirou
            if self.sessions[token].is_expired():
                del self.sessions[token]
                return False, None, "Sessão expirada"
            
            # Decodificar o token
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Atualizar último acesso da sessão
            self.sessions[token].update_last_access()
            
            return True, payload, None
        except jwt.ExpiredSignatureError:
            # Remover sessão expirada
            if token in self.sessions:
                del self.sessions[token]
            return False, None, "Token expirado"
        except jwt.InvalidTokenError:
            return False, None, "Token inválido"
    
    def logout(self, token: str) -> bool:
        """
        Encerra a sessão do usuário.
        
        Args:
            token: Token JWT da sessão a ser encerrada
            
        Returns:
            True se a sessão foi encerrada com sucesso, False caso contrário
        """
        if token in self.sessions:
            del self.sessions[token]
            return True
        return False
    
    def require_auth(self, token: str, required_role: Optional[str] = None) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Verifica se o usuário está autenticado e tem a função necessária.
        
        Args:
            token: Token JWT do usuário
            required_role: Função necessária para acessar o recurso (opcional)
            
        Returns:
            Tupla contendo (sucesso, dados_do_usuário, mensagem_de_erro)
        """
        success, payload, error = self.validate_token(token)
        
        if not success:
            return False, None, error
        
        if required_role and payload.get('role') != required_role:
            return False, None, f"Acesso negado. Função '{required_role}' necessária."
        
        return True, payload, None

# Instância global do gerenciador de autenticação
auth_manager = AuthManager()
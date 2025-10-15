"""
Gerenciamento de sessões para o sistema multi-agente.
"""
import time
from typing import Any, Dict, Optional

class Session:
    """
    Representa uma sessão de usuário ativa no sistema.
    """
    def __init__(self, user_id: int, token: str, max_idle_time: int = 3600):
        """
        Inicializa uma nova sessão.
        
        Args:
            user_id: ID do usuário
            token: Token JWT associado à sessão
            max_idle_time: Tempo máximo de inatividade em segundos (padrão: 1 hora)
        """
        self.user_id = user_id
        self.token = token
        self.created_at = time.time()
        self.last_access = time.time()
        self.max_idle_time = max_idle_time
        self.data: Dict[str, Any] = {}  # Dados adicionais da sessão
    
    def update_last_access(self) -> None:
        """Atualiza o timestamp do último acesso."""
        self.last_access = time.time()
    
    def is_expired(self) -> bool:
        """
        Verifica se a sessão expirou por inatividade.
        
        Returns:
            True se a sessão expirou, False caso contrário
        """
        return (time.time() - self.last_access) > self.max_idle_time
    
    def set_data(self, key: str, value: Any) -> None:
        """
        Armazena um valor na sessão.
        
        Args:
            key: Chave para armazenar o valor
            value: Valor a ser armazenado
        """
        self.data[key] = value
    
    def get_data(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Recupera um valor da sessão.
        
        Args:
            key: Chave do valor a ser recuperado
            default: Valor padrão se a chave não existir
            
        Returns:
            Valor armazenado ou valor padrão
        """
        return self.data.get(key, default)
    
    def clear_data(self) -> None:
        """Limpa todos os dados da sessão."""
        self.data.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a sessão em um dicionário.
        
        Returns:
            Dicionário com os dados da sessão
        """
        return {
            'user_id': self.user_id,
            'token': self.token,
            'created_at': self.created_at,
            'last_access': self.last_access,
            'max_idle_time': self.max_idle_time,
            'data': self.data
        }
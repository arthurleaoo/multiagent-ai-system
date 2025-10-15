"""
Módulo que define a classe base para todos os agentes do sistema.
"""
from abc import ABC, abstractmethod
import logging
from typing import Dict, Any, List, Optional

from src.core.genai_client import GenAIClient

class BaseAgent(ABC):
    """
    Classe base que define a interface e comportamentos comuns para todos os agentes.
    """
    
    def __init__(self, name: str, role: str, genai_client: GenAIClient):
        """
        Inicializa um agente base.
        """
        self.name = name
        self.role = role
        self.genai_client = genai_client
        self.logger = logging.getLogger(f"agent.{name}")
        self.memory: List[Dict[str, Any]] = []
        
    def add_to_memory(self, message: Dict[str, Any]) -> None:
        """Adiciona uma mensagem à memória do agente."""
        self.memory.append(message)
        
    def get_memory(self) -> List[Dict[str, Any]]:
        """Recupera a memória completa do agente."""
        return self.memory
        
    def clear_memory(self) -> None:
        """Limpa a memória do agente."""
        self.memory = []
        
    @abstractmethod
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa uma mensagem recebida e retorna uma resposta.
        """
        pass
    
    @abstractmethod
    def execute_task(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Executa uma tarefa específica do agente.
        Retorna None em caso de falha controlada.
        """
        pass

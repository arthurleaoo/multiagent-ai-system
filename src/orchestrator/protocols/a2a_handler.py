"""
Implementação do protocolo de comunicação Agent-to-Agent (A2A).
"""
from typing import Dict, Any, List, Optional
import json
import uuid
import logging
from datetime import datetime

class A2AHandler:
    """
    Gerencia o protocolo de comunicação entre agentes (A2A).
    """
    
    def __init__(self):
        """Inicializa o manipulador A2A."""
        self.logger = logging.getLogger("a2a_handler")
        self.message_registry = {}  # Registro de mensagens para rastreamento
        
    def create_message(self, 
                      sender: str, 
                      receiver: str, 
                      content: Dict[str, Any], 
                      message_type: str = "request") -> Dict[str, Any]:
        """
        Cria uma mensagem formatada para comunicação entre agentes.
        
        Args:
            sender: Identificador do agente remetente
            receiver: Identificador do agente destinatário
            content: Conteúdo da mensagem
            message_type: Tipo da mensagem (request, response, notification)
            
        Returns:
            Mensagem formatada
        """
        message_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        message = {
            "id": message_id,
            "timestamp": timestamp,
            "sender": sender,
            "receiver": receiver,
            "type": message_type,
            "content": content
        }
        
        self.logger.debug(f"Mensagem criada: {message_id} de {sender} para {receiver}")
        return message
    
    def create_response(self, 
                       original_message: Dict[str, Any], 
                       content: Dict[str, Any], 
                       status: str = "success") -> Dict[str, Any]:
        """
        Cria uma resposta para uma mensagem recebida.
        
        Args:
            original_message: Mensagem original
            content: Conteúdo da resposta
            status: Status da resposta (success, error, pending)
            
        Returns:
            Mensagem de resposta formatada
        """
        message_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        response = {
            "id": message_id,
            "timestamp": timestamp,
            "sender": original_message["receiver"],
            "receiver": original_message["sender"],
            "type": "response",
            "in_reply_to": original_message["id"],
            "status": status,
            "content": content
        }
        
        self.logger.debug(f"Resposta criada: {message_id} para mensagem {original_message['id']}")
        return response
    
    def validate_message(self, message: Dict[str, Any]) -> bool:
        """
        Valida se uma mensagem está no formato correto.
        
        Args:
            message: Mensagem a ser validada
            
        Returns:
            True se a mensagem for válida, False caso contrário
        """
        required_fields = ["id", "timestamp", "sender", "receiver", "type", "content"]
        
        # Verificar campos obrigatórios
        for field in required_fields:
            if field not in message:
                self.logger.error(f"Mensagem inválida: campo '{field}' ausente")
                return False
        
        # Verificar tipo de mensagem
        valid_types = ["request", "response", "notification"]
        if message["type"] not in valid_types:
            self.logger.error(f"Tipo de mensagem inválido: {message['type']}")
            return False
            
        # Verificar campos adicionais para respostas
        if message["type"] == "response":
            if "in_reply_to" not in message:
                self.logger.error("Mensagem de resposta sem campo 'in_reply_to'")
                return False
            if "status" not in message:
                self.logger.error("Mensagem de resposta sem campo 'status'")
                return False
        
        return True
    
    def serialize_message(self, message: Dict[str, Any]) -> str:
        """
        Serializa uma mensagem para transmissão.
        
        Args:
            message: Mensagem a ser serializada
            
        Returns:
            Mensagem serializada em formato JSON
        """
        try:
            return json.dumps(message)
        except Exception as e:
            self.logger.error(f"Erro ao serializar mensagem: {str(e)}")
            return ""
    
    def deserialize_message(self, serialized_message: str) -> Dict[str, Any]:
        """
        Deserializa uma mensagem recebida.
        
        Args:
            serialized_message: Mensagem serializada
            
        Returns:
            Mensagem deserializada
        """
        try:
            message = json.loads(serialized_message)
            if self.validate_message(message):
                return message
            else:
                return {}
        except Exception as e:
            self.logger.error(f"Erro ao deserializar mensagem: {str(e)}")
            return {}
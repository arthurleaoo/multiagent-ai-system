"""
Configurações do sistema multi-agente.
"""
import os
from typing import Dict, Any
import logging
import json
from pathlib import Path

class Config:
    """
    Gerencia as configurações do sistema.
    """
    
    def __init__(self, config_file: str = None):
        """
        Inicializa as configurações.
        
        Args:
            config_file: Caminho para o arquivo de configuração
        """
        self.logger = logging.getLogger(__name__)
        self.config_file = config_file or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            "config.json"
        )
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Carrega as configurações do arquivo.
        
        Returns:
            Configurações carregadas
        """
        default_config = {
            "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 1000,
            "log_level": "INFO"
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    loaded_config = json.load(f)
                    # Mesclar com configurações padrão
                    config = {**default_config, **loaded_config}
                    self.logger.info(f"Configurações carregadas de {self.config_file}")
                    return config
            else:
                self.logger.warning(f"Arquivo de configuração {self.config_file} não encontrado. Usando configurações padrão.")
                return default_config
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {str(e)}", exc_info=True)
            return default_config
            
    def save_config(self) -> bool:
        """
        Salva as configurações no arquivo.
        
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        try:
            # Garantir que o diretório existe
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
                
            self.logger.info(f"Configurações salvas em {self.config_file}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {str(e)}", exc_info=True)
            return False
            
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém uma configuração.
        
        Args:
            key: Chave da configuração
            default: Valor padrão caso a configuração não exista
            
        Returns:
            Valor da configuração
        """
        return self.config.get(key, default)
        
    def set(self, key: str, value: Any) -> None:
        """
        Define uma configuração.
        
        Args:
            key: Chave da configuração
            value: Valor da configuração
        """
        self.config[key] = value
        
    def get_openai_api_key(self) -> str:
        """
        Obtém a chave da API OpenAI.
        
        Returns:
            Chave da API OpenAI
        """
        return self.get("openai_api_key", os.getenv("OPENAI_API_KEY", ""))
        
    def set_openai_api_key(self, api_key: str) -> None:
        """
        Define a chave da API OpenAI.
        
        Args:
            api_key: Chave da API OpenAI
        """
        self.set("openai_api_key", api_key)
        
    def get_model(self) -> str:
        """
        Obtém o modelo a ser usado.
        
        Returns:
            Nome do modelo
        """
        return self.get("model", "gpt-3.5-turbo")
        
    def set_model(self, model: str) -> None:
        """
        Define o modelo a ser usado.
        
        Args:
            model: Nome do modelo
        """
        self.set("model", model)
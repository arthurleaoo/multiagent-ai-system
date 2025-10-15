"""
Cliente para comunicação com a API OpenAI.
"""
import os
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI  # ⚡ Correção SDK

class GenAIClient:
    """
    Cliente para interação com a API OpenAI.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo", logger=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key não fornecida e não encontrada nas variáveis de ambiente")
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.logger = logger or logging.getLogger("genai_client")

        
    def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "gpt-3.5-turbo", 
        temperature: float = 0.7, 
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Gera uma resposta usando o modelo de linguagem.
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                "content": response.choices[0].message.content,
                "role": "assistant",
                "model": model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            self.logger.error(f"Erro ao gerar resposta: {str(e)}", exc_info=True)
            return {
                "content": f"Erro ao gerar resposta: {str(e)}",
                "role": "system",
                "error": True
            }
            
    def get_embedding(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """
        Obtém o embedding de um texto.
        """
        try:
            response = self.client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            self.logger.error(f"Erro ao obter embedding: {str(e)}", exc_info=True)
            return []

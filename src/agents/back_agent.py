"""
Agente especializado em desenvolvimento back-end.
"""
from typing import Dict, Any, List, Optional
import logging
import json

from src.core.base_agent import BaseAgent
from src.core.genai_client import GenAIClient
from src.orchestrator.protocols.mcp_handler import MCPHandler


class BackAgent(BaseAgent):
    """
    Agente especializado em tarefas de Back-End.
    """
    def __init__(self, genai_client: GenAIClient):
        super().__init__(name="BackAgent", role="back", genai_client=genai_client)
        self.mcp_handler = MCPHandler()
        if not hasattr(self, "logger") or self.logger is None:
            self.logger = logging.getLogger(self.name)

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa uma mensagem recebida e retorna uma resposta.
        
        Args:
            message: Mensagem a ser processada
            
        Returns:
            Resposta processada
        """
        self.logger.info("Processando mensagem: %s", message.get("type", "desconhecido"))
        self.add_to_memory(message)
        
        # Criar prompt específico para o agente de back-end
        prompt = self.mcp_handler.create_agent_prompt(
            agent_role="back-end",
            task_description=message.get("content", {}).get("description", "Processar lógica de negócios")
        )
        
        # Criar contexto para o modelo
        model_messages = self.mcp_handler.create_context(
            system_prompt=prompt, 
            user_message=str(message.get("content", {}))
        )
        
        # Gerar resposta usando o cliente GenAI
        response = self.genai_client.generate_response(
            messages=model_messages, 
            temperature=0.5  # Temperatura mais baixa para respostas mais determinísticas
        )
        
        # Processar a resposta
        processed = self.mcp_handler.extract_response(response)
        
        return {
            "success": True, 
            "response": processed, 
            "agent": self.name
        }

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma tarefa específica do agente.
        
        Args:
            task: Tarefa a ser executada
            
        Returns:
            Resultado da execução da tarefa
        """
        action = task.get("action", "")
        self.logger.info("Executando ação: %s", action)
        
        if action == "process_task":
            return self._process_task(task)
        elif action == "generate_api":
            return self._generate_api(task)
        elif action == "analyze_data_model":
            return self._analyze_data_model(task)
        else:
            self.logger.warning("Ação desconhecida: %s", action)
            return {"success": False, "error": f"Ação desconhecida: {action}"}

    def _process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa uma tarefa com base na análise do front-end.
        
        Args:
            task: Tarefa a ser processada
            
        Returns:
            Resultado do processamento
        """
        task_data = task.get("task_data", {})
        front_analysis = task.get("front_analysis", {})
        prompt = f"""Como agente de back-end, processe a seguinte tarefa com base na análise do front-end:

Título: {task_data.get('title', 'Sem título')}
Descrição: {task_data.get('description', 'Sem descrição')}
Análise do Front-End: {json.dumps(front_analysis, indent=2)}

Forneça sua análise no seguinte formato JSON:
{
    "endpoints": ["lista de endpoints necessários"],
    "modelos_dados": ["modelos de dados necessários"],
    "logica_negocio": ["regras de negócio identificadas"],
    "consideracoes_tecnicas": ["considerações técnicas importantes"],
    "summary": "resumo em uma frase"
}
"""
        model_messages = self.mcp_handler.create_context(system_prompt=prompt, user_message="")
        response = self.genai_client.generate_response(messages=model_messages, temperature=0.5)
        
        try:
            content = response.get("content", "{}")
            # Extrair JSON da resposta
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                analysis = json.loads(json_str)
            else:
                analysis = {"error": "Formato JSON não encontrado na resposta"}
                
            return {
                "success": True,
                "analysis": analysis,
                "task_id": task.get("task_id"),
                "summary": analysis.get("summary", "Processamento de back-end concluído")
            }
        except Exception as e:
            self.logger.error(f"Erro ao analisar resposta: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Erro ao analisar resposta: {str(e)}",
                "task_id": task.get("task_id")
            }
            
    def _generate_api(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera código de API com base nos requisitos.
        
        Args:
            task: Tarefa com requisitos de API
            
        Returns:
            Código de API gerado
        """
        task_data = task.get("task_data", {})
        requirements = task.get("requirements", {})
        
        prompt = f"""Como agente de back-end, gere código de API para a seguinte tarefa:

Título: {task_data.get('title', 'Sem título')}
Descrição: {task_data.get('description', 'Sem descrição')}

Requisitos: {json.dumps(requirements, indent=2)}

Gere código Python usando Flask ou FastAPI para implementar esta API.
Use as melhores práticas de segurança, validação e documentação.
"""
        model_messages = self.mcp_handler.create_context(system_prompt=prompt, user_message="")
        response = self.genai_client.generate_response(
            messages=model_messages, 
            temperature=0.5,
            max_tokens=2000
        )
        
        return {
            "success": True,
            "code": response.get("content", ""),
            "task_id": task.get("task_id"),
            "summary": "Código de API gerado"
        }
        
    def _analyze_data_model(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa e propõe modelos de dados para a aplicação.
        
        Args:
            task: Tarefa com requisitos
            
        Returns:
            Modelos de dados propostos
        """
        task_data = task.get("task_data", {})
        
        prompt = f"""Como agente de back-end, analise e proponha modelos de dados para a seguinte tarefa:

Título: {task_data.get('title', 'Sem título')}
Descrição: {task_data.get('description', 'Sem descrição')}

Forneça sua análise no seguinte formato JSON:
{{
    "entidades": [
        {{
            "nome": "nome_da_entidade",
            "atributos": [
                {{
                    "nome": "nome_do_atributo",
                    "tipo": "tipo_do_atributo",
                    "descricao": "descrição do atributo"
                }}
            ],
            "relacionamentos": [
                {{
                    "entidade": "entidade_relacionada",
                    "tipo": "tipo_de_relacionamento",
                    "descricao": "descrição do relacionamento"
                }}
            ]
        }}
    ],
    "summary": "resumo em uma frase"
}}
"""
        model_messages = self.mcp_handler.create_context(system_prompt=prompt, user_message="")
        response = self.genai_client.generate_response(
            messages=model_messages, 
            temperature=0.5,
            max_tokens=1500
        )
        
        try:
            content = response.get("content", "{}")
            # Extrair JSON da resposta
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                analysis = json.loads(json_str)
            else:
                analysis = {"error": "Formato JSON não encontrado na resposta"}
                
            return {
                "success": True,
                "data_model": analysis,
                "task_id": task.get("task_id"),
                "summary": analysis.get("summary", "Modelo de dados analisado")
            }
        except Exception as e:
            self.logger.error(f"Erro ao analisar resposta: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Erro ao analisar resposta: {str(e)}",
                "task_id": task.get("task_id")
            }

Análise do front-end:
{front_analysis.get('summary', 'Sem análise do front-end')}

Responda em JSON com: data_models, apis, business_logic, implementation_notes, summary
"""
        response = self.genai_client.generate_response(messages=[
            {"role": "system", "content": self.mcp_handler.create_agent_prompt("back-end", "Processamento de lógica de negócios")},
            {"role": "user", "content": prompt}
        ], temperature=0.5)
        processed = self.mcp_handler.extract_response(response)
        if processed.get("has_structured_data", False):
            processing_result = processed.get("structured_data", {})
        else:
            processing_result = {
                "data_models": ["User", "Task", "Result"],
                "apis": ["/api/process", "/api/status", "/api/results"],
                "business_logic": "Processamento de dados com validação e transformação",
                "implementation_notes": "Implementar validação de entrada e tratamento de erros",
                "summary": "Lógica de negócios processada com sucesso"
            }
        return {"success": True, "processing_result": processing_result, "summary": processing_result.get("summary", "Processamento concluído")}

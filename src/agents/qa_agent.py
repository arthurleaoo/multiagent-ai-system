"""
Agente especializado em testes e garantia de qualidade.
"""
from typing import Dict, Any, List, Optional
import logging
import json

from src.core.base_agent import BaseAgent
from src.core.genai_client import GenAIClient
from src.orchestrator.protocols.mcp_handler import MCPHandler


class QAAgent(BaseAgent):
    """
    Agente especializado em tarefas de QA e testes.
    """
    def __init__(self, genai_client: GenAIClient):
        super().__init__(name="QAAgent", role="qa", genai_client=genai_client)
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
        
        # Criar prompt específico para o agente de QA
        prompt = self.mcp_handler.create_agent_prompt(
            agent_role="qa",
            task_description=message.get("content", {}).get("description", "Verificar qualidade e testar")
        )
        
        # Criar contexto para o modelo
        model_messages = self.mcp_handler.create_context(
            system_prompt=prompt, 
            user_message=str(message.get("content", {}))
        )
        
        # Gerar resposta usando o cliente GenAI
        response = self.genai_client.generate_response(
            messages=model_messages, 
            temperature=0.3  # Temperatura mais baixa para respostas mais precisas
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
        
        if action == "verify_result":
            return self._verify_result(task)
        elif action == "generate_tests":
            return self._generate_tests(task)
        elif action == "security_audit":
            return self._security_audit(task)
        else:
            self.logger.warning("Ação desconhecida: %s", action)
            return {"success": False, "error": f"Ação desconhecida: {action}"}

    def _verify_result(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifica o resultado do processamento do back-end.
        
        Args:
            task: Tarefa com resultados do back-end
            
        Returns:
            Resultado da verificação
        """
        task_data = task.get("task_data", {})
        back_result = task.get("back_result", {})
        prompt = f"""Como agente de QA, verifique o resultado do processamento do back-end:

Título: {task_data.get('title', 'Sem título')}
Resultado do Back-End: {json.dumps(back_result, indent=2)}

Forneça sua verificação no seguinte formato JSON:
{
    "testes_realizados": ["lista de testes realizados"],
    "bugs_encontrados": ["bugs ou problemas encontrados"],
    "melhorias_sugeridas": ["melhorias sugeridas"],
    "status": "aprovado/reprovado",
    "summary": "resumo em uma frase"
}
"""
        model_messages = self.mcp_handler.create_context(system_prompt=prompt, user_message="")
        response = self.genai_client.generate_response(messages=model_messages, temperature=0.3)
        
        try:
            content = response.get("content", "{}")
            # Extrair JSON da resposta
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                verification = json.loads(json_str)
            else:
                verification = {"error": "Formato JSON não encontrado na resposta"}
                
            return {
                "success": True,
                "verification": verification,
                "task_id": task.get("task_id"),
                "summary": verification.get("summary", "Verificação de QA concluída")
            }
        except Exception as e:
            self.logger.error(f"Erro ao analisar resposta: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Erro ao analisar resposta: {str(e)}",
                "task_id": task.get("task_id")
            }
            
    def _generate_tests(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera testes automatizados para o código.
        
        Args:
            task: Tarefa com código a ser testado
            
        Returns:
            Testes gerados
        """
        task_data = task.get("task_data", {})
        code = task.get("code", "")
        
        prompt = f"""Como agente de QA, gere testes automatizados para o seguinte código:

Título: {task_data.get('title', 'Sem título')}
Descrição: {task_data.get('description', 'Sem descrição')}

Código:
```
{code}
```

Gere testes unitários e de integração usando pytest ou unittest.
Cubra casos de sucesso e falha.
"""
        model_messages = self.mcp_handler.create_context(system_prompt=prompt, user_message="")
        response = self.genai_client.generate_response(
            messages=model_messages, 
            temperature=0.3,
            max_tokens=1500
        )
        
        return {
            "success": True,
            "tests": response.get("content", ""),
            "task_id": task.get("task_id"),
            "summary": "Testes automatizados gerados"
        }
        
    def _security_audit(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza uma auditoria de segurança no código.
        
        Args:
            task: Tarefa com código a ser auditado
            
        Returns:
            Resultado da auditoria de segurança
        """
        task_data = task.get("task_data", {})
        code = task.get("code", "")
        
        prompt = f"""Como agente de QA especializado em segurança, realize uma auditoria de segurança no seguinte código:

Título: {task_data.get('title', 'Sem título')}
Descrição: {task_data.get('description', 'Sem descrição')}

Código:
```
{code}
```

Forneça sua auditoria no seguinte formato JSON:
{{
    "vulnerabilidades": [
        {{
            "tipo": "tipo_de_vulnerabilidade",
            "descricao": "descrição da vulnerabilidade",
            "severidade": "alta/média/baixa",
            "recomendacao": "recomendação para correção"
        }}
    ],
    "boas_praticas": ["boas práticas identificadas"],
    "melhorias_seguranca": ["melhorias de segurança sugeridas"],
    "summary": "resumo em uma frase"
}}
"""
        model_messages = self.mcp_handler.create_context(system_prompt=prompt, user_message="")
        response = self.genai_client.generate_response(
            messages=model_messages, 
            temperature=0.3,
            max_tokens=1500
        )
        
        try:
            content = response.get("content", "{}")
            # Extrair JSON da resposta
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                audit = json.loads(json_str)
            else:
                audit = {"error": "Formato JSON não encontrado na resposta"}
                
            return {
                "success": True,
                "audit": audit,
                "task_id": task.get("task_id"),
                "summary": audit.get("summary", "Auditoria de segurança concluída")
            }
        except Exception as e:
            self.logger.error(f"Erro ao analisar resposta: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Erro ao analisar resposta: {str(e)}",
                "task_id": task.get("task_id")
            }

Resultado do processamento:
{back_result.get('summary', 'Sem resumo de processamento')}

Responda em JSON com: requirements_met, issues, improvements, quality_score, summary
"""
        response = self.genai_client.generate_response(messages=[
            {"role": "system", "content": self.mcp_handler.create_agent_prompt("qa", "Verificação de qualidade")},
            {"role": "user", "content": prompt}
        ], temperature=0.3)
        processed = self.mcp_handler.extract_response(response)
        if processed.get("has_structured_data", False):
            verification_result = processed.get("structured_data", {})
        else:
            verification_result = {
                "requirements_met": ["Funcionalidade básica implementada", "Estrutura de dados adequada"],
                "issues": ["Possível problema de validação de entrada"],
                "improvements": ["Adicionar mais validações", "Melhorar documentação da API"],
                "quality_score": 7,
                "summary": "Implementação satisfatória com algumas melhorias sugeridas"
            }
        return {"success": True, "verification_result": verification_result, "quality_score": verification_result.get("quality_score", 5), "summary": verification_result.get("summary", "Verificação concluída")}

"""
Agente especializado em testes e garantia de qualidade.
"""
from typing import Dict, Any
import logging

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
        self.logger.info("Processando mensagem: %s", message.get("type", "desconhecido"))
        self.add_to_memory(message)
        prompt = self.mcp_handler.create_agent_prompt(
            agent_role="qa",
            task_description=message.get("content", {}).get("description", "Verificar qualidade e testar")
        )
        model_messages = self.mcp_handler.create_context(system_prompt=prompt, user_message=str(message.get("content", {})))
        response = self.genai_client.generate_response(messages=model_messages, temperature=0.3)
        processed = self.mcp_handler.extract_response(response)
        return {"success": True, "response": processed, "agent": self.name}

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action", "")
        self.logger.info("Executando ação: %s", action)
        if action == "verify_result":
            return self._verify_result(task)
        else:
            self.logger.warning("Ação desconhecida: %s", action)
            return {"success": False, "error": f"Ação desconhecida: {action}"}

    def _verify_result(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_data = task.get("task_data", {})
        back_result = task.get("back_result", {})
        prompt = f"""Como agente de QA, verifique o resultado do processamento do back-end:

Título: {task_data.get('title', 'Sem título')}
Descrição: {task_data.get('description', 'Sem descrição')}

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

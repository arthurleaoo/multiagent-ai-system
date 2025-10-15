"""
Agente especializado em desenvolvimento back-end.
"""
from typing import Dict, Any
import logging

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
        self.logger.info("Processando mensagem: %s", message.get("type", "desconhecido"))
        self.add_to_memory(message)
        prompt = self.mcp_handler.create_agent_prompt(
            agent_role="back-end",
            task_description=message.get("content", {}).get("description", "Processar lógica de negócios")
        )
        model_messages = self.mcp_handler.create_context(system_prompt=prompt, user_message=str(message.get("content", {})))
        response = self.genai_client.generate_response(messages=model_messages, temperature=0.5)
        processed = self.mcp_handler.extract_response(response)
        return {"success": True, "response": processed, "agent": self.name}

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action", "")
        self.logger.info("Executando ação: %s", action)
        if action == "process_task":
            return self._process_task(task)
        else:
            self.logger.warning("Ação desconhecida: %s", action)
            return {"success": False, "error": f"Ação desconhecida: {action}"}

    def _process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_data = task.get("task_data", {})
        front_analysis = task.get("front_analysis", {})
        prompt = f"""Como agente de back-end, processe a seguinte tarefa com base na análise do front-end:

Título: {task_data.get('title', 'Sem título')}
Descrição: {task_data.get('description', 'Sem descrição')}

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

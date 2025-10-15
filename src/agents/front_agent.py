"""
Agente especializado em desenvolvimento front-end.
"""
from typing import Dict, Any
import logging

from src.core.base_agent import BaseAgent
from src.core.genai_client import GenAIClient
from src.orchestrator.protocols.mcp_handler import MCPHandler


class FrontAgent(BaseAgent):
    """
    Agente especializado em tarefas de Front-End.
    """
    def __init__(self, genai_client: GenAIClient):
        super().__init__(name="FrontAgent", role="front", genai_client=genai_client)
        self.mcp_handler = MCPHandler()
        if not hasattr(self, "logger") or self.logger is None:
            self.logger = logging.getLogger(self.name)

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Processando mensagem: %s", message.get("type", "desconhecido"))
        self.add_to_memory(message)
        prompt = self.mcp_handler.create_agent_prompt(
            agent_role="front-end",
            task_description=message.get("content", {}).get("description", "Analisar requisitos de interface")
        )
        model_messages = self.mcp_handler.create_context(system_prompt=prompt, user_message=str(message.get("content", {})))
        response = self.genai_client.generate_response(messages=model_messages, temperature=0.7)
        processed_response = self.mcp_handler.extract_response(response)
        return {"success": True, "response": processed_response, "agent": self.name}

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        action = task.get("action", "")
        self.logger.info("Executando ação: %s", action)
        if action == "analyze_task":
            return self._analyze_task(task)
        elif action == "prepare_response":
            return self._prepare_response(task)
        else:
            self.logger.warning("Ação desconhecida: %s", action)
            return {"success": False, "error": f"Ação desconhecida: {action}"}

    def _analyze_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_data = task.get("task_data", {})
        prompt = f"""Como agente de front-end, analise a seguinte tarefa e identifique os requisitos de interface:

Título: {task_data.get('title', 'Sem título')}
Descrição: {task_data.get('description', 'Sem descrição')}

Forneça uma análise detalhada dos requisitos de interface, componentes necessários e considerações de UX/UI.
Responda em formato JSON com os campos: ui_components, user_flows, design_considerations, summary
"""
        response = self.genai_client.generate_response(messages=[
            {"role": "system", "content": self.mcp_handler.create_agent_prompt("front-end", "Análise de requisitos de interface")},
            {"role": "user", "content": prompt}
        ], temperature=0.7)
        processed = self.mcp_handler.extract_response(response)
        if processed.get("has_structured_data", False):
            analysis = processed.get("structured_data", {})
        else:
            analysis = {
                "ui_components": ["Formulário de entrada", "Botões de ação", "Área de exibição de resultados"],
                "user_flows": ["Entrada de dados -> Processamento -> Visualização de resultados"],
                "design_considerations": ["Layout responsivo", "Acessibilidade", "Feedback visual"],
                "summary": "Interface básica para processamento e visualização de dados"
            }
        return {"success": True, "analysis": analysis, "summary": analysis.get("summary", "Análise concluída")}

    def _prepare_response(self, task: Dict[str, Any]) -> Dict[str, Any]:
        qa_result = task.get("qa_result", {})
        task_data = task.get("task_data", {})
        prompt = f"""Como agente de front-end, prepare uma resposta final para o usuário:

Título: {task_data.get('title', 'Sem título')}
Resultado da verificação: {qa_result.get('summary', 'Sem resumo')}
Pontuação de qualidade: {qa_result.get('quality_score', 'N/A')}
"""
        response = self.genai_client.generate_response(messages=[
            {"role": "system", "content": self.mcp_handler.create_agent_prompt("front-end", "Preparação de resposta final")},
            {"role": "user", "content": prompt}
        ], temperature=0.7)
        processed = self.mcp_handler.extract_response(response)
        return {"success": True, "user_response": processed.get("content", "Tarefa processada com sucesso."), "summary": "Resposta final preparada"}

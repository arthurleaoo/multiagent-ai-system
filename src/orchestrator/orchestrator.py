"""
Orquestrador central do sistema multi-agente.
"""
import logging
from typing import Dict, Any, List

from src.core.base_agent import BaseAgent
from src.core.genai_client import GenAIClient
from src.orchestrator.protocols.mcp_handler import MCPHandler
from src.orchestrator.protocols.a2a_handler import A2AHandler
from src.data.database import init_db, create_task, log_interaction, update_task_status, get_task

# Import correto dos agentes (nomes padronizados)
from src.agents.front_agent import FrontAgent
from src.agents.back_agent import BackAgent
from src.agents.qa_agent import QAAgent


class Orchestrator:

    def __init__(self, front_agent, back_agent, qa_agent, db, logger):
        self.front_agent = front_agent
        self.back_agent = back_agent
        self.qa_agent = qa_agent
        self.db = db
        self.logger = logger


    def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa uma tarefa com fluxo: front -> back -> qa -> front (final)."""
        self.logger.info("Processando tarefa: %s", task_data.get("title"))

        # 1) criar registro da task
        task_id = create_task(
            title=task_data.get("title", "Sem título"),
            description=task_data.get("description", ""),
            user_id=task_data.get("user_id", 0),
            project_id=task_data.get("project_id")
        )

        try:
            # 2) Front analyze
            front_result = self._execute_agent_task("front_agent", {
                "action": "analyze_task",
                "task_id": task_id,
                "task_data": task_data
            })
            log_interaction(task_id, "front_agent", f"Análise inicial: {front_result.get('summary','N/A')}")

            # 3) Back process
            back_result = self._execute_agent_task("back_agent", {
                "action": "process_task",
                "task_id": task_id,
                "front_analysis": front_result,
                "task_data": task_data
            })
            log_interaction(task_id, "back_agent", f"Processamento: {back_result.get('summary','N/A')}")

            # 4) QA verify
            qa_result = self._execute_agent_task("qa_agent", {
                "action": "verify_result",
                "task_id": task_id,
                "back_result": back_result,
                "task_data": task_data
            })
            log_interaction(task_id, "qa_agent", f"Verificação: {qa_result.get('summary','N/A')}")

            # 5) Front prepare final response
            final_result = self._execute_agent_task("front_agent", {
                "action": "prepare_response",
                "task_id": task_id,
                "qa_result": qa_result,
                "task_data": task_data
            })
            log_interaction(task_id, "front_agent", f"Resposta final: {final_result.get('summary','N/A')}")

            # 6) update status
            update_task_status(task_id, "completed", output_gerado=str(final_result))
            return final_result

        except Exception as exc:
            self.logger.exception("Erro ao processar tarefa: %s", exc)
            log_interaction(task_id, "system", f"Erro: {str(exc)}")
            update_task_status(task_id, "failed")
            return {"success": False, "error": str(exc)}

    def _execute_agent_task(self, agent_name_key: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        agent_name_key é a chave usada internamente (ex: "front_agent").
        Este método tenta localizar um agente com esse nome; se não encontrar,
        pesquisa por correspondência parcial (flexibilidade).
        """
        # busca exata
        if agent_name_key in self.agents:
            agent = self.agents[agent_name_key]
            return agent.execute_task(task_data)

        # busca por correspondência parcial (ex: "front_agent" -> nome "front")
        for name, agent in self.agents.items():
            if agent_name_key.lower() in name.lower() or name.lower() in agent_name_key.lower():
                return agent.execute_task(task_data)

        raise ValueError(f"Agente não encontrado: {agent_name_key}")

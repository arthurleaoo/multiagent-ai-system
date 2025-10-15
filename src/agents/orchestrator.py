import logging
import uuid
from typing import Dict, Any, Optional

from src.agents.front_agent import FrontAgent
from src.agents.back_agent import BackAgent
from src.agents.qa_agent import QAAgent

class Orchestrator:
    """
    Orquestrador responsável por coordenar os agentes especializados.
    """
    
    def __init__(self, front_agent: FrontAgent, back_agent: BackAgent, qa_agent: QAAgent):
        """
        Inicializa o orquestrador com os agentes especializados.
        
        Args:
            front_agent: Agente especializado em front-end
            back_agent: Agente especializado em back-end
            qa_agent: Agente especializado em QA
        """
        self.front_agent = front_agent
        self.back_agent = back_agent
        self.qa_agent = qa_agent
        self.logger = logging.getLogger(__name__)
        
    def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa uma tarefa utilizando os agentes especializados.
        
        Args:
            task_data: Dados da tarefa a ser processada
            
        Returns:
            Resultado do processamento da tarefa
        """
        # Criar ID único para a tarefa
        task_id = str(uuid.uuid4())
        
        # Criar tarefa com dados recebidos
        task = {
            "task_id": task_id,
            "task_data": task_data,
            "status": "iniciada"
        }
        
        self.logger.info(f"Iniciando processamento da tarefa {task_id}")
        
        try:
            # Etapa 1: Front-end analisa a tarefa
            self.logger.info(f"Enviando tarefa para análise pelo agente de front-end")
            front_result = self.front_agent.execute_task(task, "analyze_task")
            
            if not front_result.get("success", False):
                return {
                    "success": False,
                    "error": front_result.get("error", "Erro na análise de front-end"),
                    "task_id": task_id
                }
                
            task["front_analysis"] = front_result.get("analysis", {})
            task["status"] = "analisada_front"
            
            # Etapa 2: Back-end processa a tarefa
            self.logger.info(f"Enviando tarefa para processamento pelo agente de back-end")
            back_result = self.back_agent.execute_task(task, "process_task")
            
            if not back_result.get("success", False):
                return {
                    "success": False,
                    "error": back_result.get("error", "Erro no processamento de back-end"),
                    "task_id": task_id
                }
                
            task["back_result"] = back_result
            task["status"] = "processada_back"
            
            # Etapa 3: QA verifica o resultado
            self.logger.info(f"Enviando resultado para verificação pelo agente de QA")
            qa_result = self.qa_agent.execute_task(task, "verify_result")
            
            if not qa_result.get("success", False):
                return {
                    "success": False,
                    "error": qa_result.get("error", "Erro na verificação de QA"),
                    "task_id": task_id
                }
                
            task["qa_result"] = qa_result
            task["status"] = "verificada_qa"
            
            # Etapa 4: Front-end prepara a resposta final
            self.logger.info(f"Enviando para preparação da resposta final pelo agente de front-end")
            final_result = self.front_agent.execute_task(task, "prepare_response")
            
            if not final_result.get("success", False):
                return {
                    "success": False,
                    "error": final_result.get("error", "Erro na preparação da resposta final"),
                    "task_id": task_id
                }
                
            task["final_result"] = final_result
            task["status"] = "concluída"
            
            # Retornar resultado final
            return {
                "success": True,
                "task_id": task_id,
                "result": final_result.get("response", {}),
                "status": "concluída"
            }
            
        except Exception as e:
            self.logger.error(f"Erro no processamento da tarefa {task_id}: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Erro no processamento: {str(e)}",
                "task_id": task_id,
                "status": "erro"
            }
            
    def generate_code(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera código completo para um sistema baseado na descrição.
        
        Args:
            task_data: Dados da tarefa com descrição do sistema
            
        Returns:
            Código gerado para o sistema
        """
        # Criar ID único para a tarefa
        task_id = str(uuid.uuid4())
        
        # Criar tarefa com dados recebidos
        task = {
            "task_id": task_id,
            "task_data": task_data,
            "status": "iniciada"
        }
        
        self.logger.info(f"Iniciando geração de código para a tarefa {task_id}")
        
        try:
            # Etapa 1: Back-end analisa o modelo de dados
            self.logger.info(f"Analisando modelo de dados pelo agente de back-end")
            data_model = self.back_agent.execute_task(task, "analyze_data_model")
            
            if not data_model.get("success", False):
                return {
                    "success": False,
                    "error": data_model.get("error", "Erro na análise do modelo de dados"),
                    "task_id": task_id
                }
                
            task["data_model"] = data_model.get("model", {})
            
            # Etapa 2: Back-end gera API
            self.logger.info(f"Gerando API pelo agente de back-end")
            api_code = self.back_agent.execute_task(task, "generate_api")
            
            if not api_code.get("success", False):
                return {
                    "success": False,
                    "error": api_code.get("error", "Erro na geração da API"),
                    "task_id": task_id
                }
                
            task["api_code"] = api_code.get("code", "")
            
            # Etapa 3: Front-end gera UI
            self.logger.info(f"Gerando UI pelo agente de front-end")
            ui_code = self.front_agent.execute_task(task, "generate_ui_code")
            
            if not ui_code.get("success", False):
                return {
                    "success": False,
                    "error": ui_code.get("error", "Erro na geração da UI"),
                    "task_id": task_id
                }
                
            task["ui_code"] = ui_code.get("code", "")
            
            # Etapa 4: QA gera testes
            self.logger.info(f"Gerando testes pelo agente de QA")
            tests = self.qa_agent.execute_task(task, "generate_tests")
            
            if not tests.get("success", False):
                return {
                    "success": False,
                    "error": tests.get("error", "Erro na geração de testes"),
                    "task_id": task_id
                }
                
            task["tests"] = tests.get("tests", "")
            
            # Etapa 5: QA realiza auditoria de segurança
            self.logger.info(f"Realizando auditoria de segurança pelo agente de QA")
            security = self.qa_agent.execute_task(task, "security_audit")
            
            if not security.get("success", False):
                return {
                    "success": False,
                    "error": security.get("error", "Erro na auditoria de segurança"),
                    "task_id": task_id
                }
                
            task["security"] = security.get("audit", {})
            
            # Compilar resultado final
            result = {
                "success": True,
                "task_id": task_id,
                "backend": {
                    "data_model": task.get("data_model", {}),
                    "api_code": task.get("api_code", "")
                },
                "frontend": {
                    "ui_code": task.get("ui_code", "")
                },
                "qa": {
                    "tests": task.get("tests", ""),
                    "security": task.get("security", {})
                },
                "status": "concluída"
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro na geração de código para a tarefa {task_id}: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Erro na geração de código: {str(e)}",
                "task_id": task_id,
                "status": "erro"
            }
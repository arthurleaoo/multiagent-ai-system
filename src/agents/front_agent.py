"""
Agente especializado em desenvolvimento front-end.
"""
from typing import Dict, Any, Optional, List
import logging
import json

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
        """
        Processa uma mensagem recebida e retorna uma resposta.
        
        Args:
            message: Mensagem a ser processada
            
        Returns:
            Resposta processada
        """
        self.logger.info("Processando mensagem: %s", message.get("type", "desconhecido"))
        self.add_to_memory(message)
        
        # Criar prompt específico para o agente de front-end
        prompt = self.mcp_handler.create_agent_prompt(
            agent_role="front-end",
            task_description=message.get("content", {}).get("description", "Analisar requisitos de interface")
        )
        
        # Criar contexto para o modelo
        model_messages = self.mcp_handler.create_context(
            system_prompt=prompt, 
            user_message=str(message.get("content", {}))
        )
        
        # Gerar resposta usando o cliente GenAI
        response = self.genai_client.generate_response(
            messages=model_messages, 
            temperature=0.7
        )
        
        # Processar a resposta
        processed_response = self.mcp_handler.extract_response(response)
        
        return {
            "success": True, 
            "response": processed_response, 
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
        
        if action == "analyze_task":
            return self._analyze_task(task)
        elif action == "prepare_response":
            return self._prepare_response(task)
        elif action == "generate_ui_code":
            return self._generate_ui_code(task)
        else:
            self.logger.warning("Ação desconhecida: %s", action)
            return {"success": False, "error": f"Ação desconhecida: {action}"}

    def _analyze_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa uma tarefa e identifica requisitos de interface.
        
        Args:
            task: Tarefa a ser analisada
            
        Returns:
            Análise da tarefa
        """
        task_data = task.get("task_data", {})
        prompt = f"""Como agente de front-end, analise a seguinte tarefa e identifique os requisitos de interface:

Título: {task_data.get('title', 'Sem título')}
Descrição: {task_data.get('description', 'Sem descrição')}

Forneça sua análise no seguinte formato JSON:
{{
    "componentes": ["lista de componentes UI necessários"],
    "tecnologias": ["tecnologias recomendadas"],
    "requisitos_ui": ["requisitos específicos de UI"],
    "consideracoes": ["considerações importantes"],
    "summary": "resumo em uma frase"
}}
"""
        model_messages = self.mcp_handler.create_context(system_prompt=prompt, user_message="")
        response = self.genai_client.generate_response(messages=model_messages, temperature=0.7)
        
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
                "summary": analysis.get("summary", "Análise de interface concluída")
            }
        except Exception as e:
            self.logger.error(f"Erro ao analisar resposta: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Erro ao analisar resposta: {str(e)}",
                "task_id": task.get("task_id")
            }
            
    def _prepare_response(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepara a resposta final com base nos resultados do QA.
        
        Args:
            task: Tarefa com resultados do QA
            
        Returns:
            Resposta final formatada
        """
        task_data = task.get("task_data", {})
        qa_result = task.get("qa_result", {})
        
        prompt = f"""Como agente de front-end, prepare a resposta final para o usuário com base nos resultados do QA:

Título: {task_data.get('title', 'Sem título')}
Descrição: {task_data.get('description', 'Sem descrição')}

Resultados QA: {json.dumps(qa_result, indent=2)}

Forneça uma resposta completa que inclua:
1. Um resumo do que foi implementado
2. Os componentes de interface criados
3. Instruções de uso
4. Quaisquer considerações importantes

Formate sua resposta em HTML simples para melhor visualização.
"""
        model_messages = self.mcp_handler.create_context(system_prompt=prompt, user_message="")
        response = self.genai_client.generate_response(messages=model_messages, temperature=0.7)
        
        return {
            "success": True,
            "response": response.get("content", ""),
            "task_id": task.get("task_id"),
            "summary": "Resposta final preparada"
        }
        
    def _generate_ui_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera código de interface com base nos requisitos.
        
        Args:
            task: Tarefa com requisitos de interface
            
        Returns:
            Código de interface gerado
        """
        task_data = task.get("task_data", {})
        requirements = task.get("requirements", {})
        
        prompt = f"""Como agente de front-end, gere código de interface para a seguinte tarefa:

Título: {task_data.get('title', 'Sem título')}
Descrição: {task_data.get('description', 'Sem descrição')}

Requisitos: {json.dumps(requirements, indent=2)}

Gere código HTML, CSS e JavaScript moderno para implementar esta interface.
Use as melhores práticas de acessibilidade e responsividade.
"""
        model_messages = self.mcp_handler.create_context(system_prompt=prompt, user_message="")
        response = self.genai_client.generate_response(
            messages=model_messages, 
            temperature=0.7,
            max_tokens=2000
        )
        
        return {
            "success": True,
            "code": response.get("content", ""),
            "task_id": task.get("task_id"),
            "summary": "Código de interface gerado"
        }

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

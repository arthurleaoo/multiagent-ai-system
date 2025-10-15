"""
Implementação do Model Context Protocol (MCP).
"""
from typing import Dict, Any, List, Optional
import json
import logging

class MCPHandler:
    """
    Gerencia o protocolo de contexto do modelo (MCP) para comunicação com modelos de IA.
    """
    
    def __init__(self):
        """Inicializa o manipulador MCP."""
        self.logger = logging.getLogger("mcp_handler")
        
    def create_context(self, 
                      system_prompt: str, 
                      user_message: str, 
                      history: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """
        Cria um contexto formatado para envio ao modelo.
        
        Args:
            system_prompt: Instrução do sistema
            user_message: Mensagem do usuário
            history: Histórico de conversas anteriores (opcional)
            
        Returns:
            Lista de mensagens formatadas para a API
        """
        messages = []
        
        # Adicionar prompt do sistema
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Adicionar histórico se existir
        if history:
            messages.extend(history)
            
        # Adicionar mensagem do usuário
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
        
    def create_agent_prompt(self, agent_role: str, task_description: str) -> str:
        """
        Cria um prompt de sistema específico para um agente.
        
        Args:
            agent_role: Papel do agente (front-end, back-end, qa)
            task_description: Descrição da tarefa a ser realizada
            
        Returns:
            Prompt de sistema formatado
        """
        prompts = {
            "front-end": f"""Você é um agente especializado em desenvolvimento front-end.
Sua tarefa é: {task_description}
Foque em criar interfaces de usuário intuitivas, responsivas e acessíveis.
Use as melhores práticas de HTML, CSS e JavaScript moderno.""",

            "back-end": f"""Você é um agente especializado em desenvolvimento back-end.
Sua tarefa é: {task_description}
Foque em criar APIs robustas, seguras e escaláveis.
Implemente autenticação adequada e valide todas as entradas.""",

            "qa": f"""Você é um agente especializado em testes e garantia de qualidade.
Sua tarefa é: {task_description}
Foque em identificar bugs, problemas de segurança e melhorias de desempenho.
Sugira testes unitários, de integração e end-to-end quando apropriado."""
        }
        
        return prompts.get(agent_role, f"Você é um agente de IA. Sua tarefa é: {task_description}")
    
    def format_tool_calls(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Formata ferramentas para uso com a API OpenAI.
        
        Args:
            tools: Lista de definições de ferramentas
            
        Returns:
            Lista formatada para a API
        """
        formatted_tools = []
        for tool in tools:
            formatted_tool = {
                "type": "function",
                "function": {
                    "name": tool.get("name", ""),
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {})
                }
            }
            formatted_tools.append(formatted_tool)
        return formatted_tools
    
    def parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa a resposta do modelo e extrai informações relevantes.
        
        Args:
            response: Resposta completa do modelo
            
        Returns:
            Dados estruturados da resposta
        """
        try:
            # Extrair conteúdo da mensagem
            content = response.choices[0].message.content
            
            # Verificar se há chamadas de função
            tool_calls = response.choices[0].message.get("tool_calls", [])
            
            result = {
                "content": content,
                "has_tool_calls": len(tool_calls) > 0,
                "tool_calls": []
            }
            
            # Processar chamadas de função se existirem
            if result["has_tool_calls"]:
                for tool_call in tool_calls:
                    try:
                        function_call = tool_call.get("function", {})
                        result["tool_calls"].append({
                            "name": function_call.get("name", ""),
                            "arguments": json.loads(function_call.get("arguments", "{}"))
                        })
                    except json.JSONDecodeError:
                        self.logger.error(f"Erro ao decodificar argumentos da função: {function_call.get('arguments', '')}")
            
            return result
        except Exception as e:
            self.logger.error(f"Erro ao analisar resposta do modelo: {str(e)}")
            return {"content": "Erro ao processar resposta", "error": str(e)}
    
    def extract_response(self, model_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrai e processa a resposta do modelo.
        
        Args:
            model_response: Resposta bruta do modelo
            
        Returns:
            Resposta processada
        """
        try:
            content = model_response.get("content", "")
            
            # Tentar extrair JSON se existir
            try:
                # Procurar por blocos de código JSON
                json_start = content.find("```json")
                json_end = content.find("```", json_start + 7)
                
                if json_start != -1 and json_end != -1:
                    json_content = content[json_start + 7:json_end].strip()
                    parsed_data = json.loads(json_content)
                    return {
                        "content": content,
                        "structured_data": parsed_data,
                        "has_structured_data": True
                    }
            except Exception as e:
                self.logger.debug(f"Não foi possível extrair JSON: {str(e)}")
            
            # Retornar apenas o conteúdo se não houver JSON
            return {
                "content": content,
                "has_structured_data": False
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair resposta: {str(e)}")
            return {
                "content": "Erro ao processar resposta do modelo",
                "error": str(e),
                "has_structured_data": False
            }
    
    def create_agent_prompt(self, agent_role: str, task_description: str) -> str:
        """
        Cria um prompt específico para um agente com base em seu papel.
        
        Args:
            agent_role: Papel do agente (front-end, back-end, qa)
            task_description: Descrição da tarefa
            
        Returns:
            Prompt formatado para o agente
        """
        base_prompt = f"""Você é um agente especializado em {agent_role} em um sistema multi-agente.
Sua tarefa atual é: {task_description}

"""
        
        if agent_role == "front-end":
            base_prompt += """Como agente de front-end, você deve:
1. Analisar requisitos de interface do usuário
2. Projetar componentes visuais e interações
3. Considerar a experiência do usuário e acessibilidade
4. Comunicar claramente suas decisões de design

Responda em formato JSON quando possível, incluindo:
- "analysis": sua análise dos requisitos
- "components": componentes de UI propostos
- "interactions": fluxos de interação
- "summary": resumo das suas conclusões
"""
        
        elif agent_role == "back-end":
            base_prompt += """Como agente de back-end, você deve:
1. Analisar requisitos técnicos e de dados
2. Projetar APIs, modelos de dados e lógica de negócios
3. Considerar segurança, desempenho e escalabilidade
4. Implementar soluções robustas e testáveis

Responda em formato JSON quando possível, incluindo:
- "analysis": sua análise técnica
- "data_models": modelos de dados propostos
- "apis": endpoints e funcionalidades
- "logic": lógica de negócios principal
- "summary": resumo das suas conclusões
"""
        
        elif agent_role == "qa":
            base_prompt += """Como agente de QA, você deve:
1. Verificar se os requisitos foram atendidos
2. Identificar possíveis problemas ou bugs
3. Sugerir melhorias e otimizações
4. Garantir a qualidade geral da solução

Responda em formato JSON quando possível, incluindo:
- "verification": resultados da verificação
- "issues": problemas encontrados
- "improvements": sugestões de melhoria
- "quality_score": pontuação de qualidade (0-10)
- "summary": resumo das suas conclusões
"""
        
        return base_prompt
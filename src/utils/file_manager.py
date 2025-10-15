import os
import json
import shutil
from datetime import datetime

class FileManager:
    """
    Gerencia a criação, leitura e manipulação de arquivos gerados pelos agentes.
    """
    
    def __init__(self, base_storage_path):
        """
        Inicializa o gerenciador de arquivos.
        
        Args:
            base_storage_path (str): Caminho base para armazenamento de arquivos
        """
        self.base_path = base_storage_path
        os.makedirs(self.base_path, exist_ok=True)
    
    def create_task_directory(self, task_id):
        """
        Cria um diretório para uma tarefa específica.
        
        Args:
            task_id (int): ID da tarefa
            
        Returns:
            str: Caminho do diretório criado
        """
        task_dir = os.path.join(self.base_path, f"task_{task_id}")
        os.makedirs(task_dir, exist_ok=True)
        return task_dir
    
    def save_text_file(self, task_id, filename, content, agent_type=None):
        """
        Salva conteúdo de texto em um arquivo.
        
        Args:
            task_id (int): ID da tarefa
            filename (str): Nome do arquivo
            content (str): Conteúdo a ser salvo
            agent_type (str, optional): Tipo do agente (front, back, qa)
            
        Returns:
            str: Caminho completo do arquivo salvo
        """
        task_dir = self.create_task_directory(task_id)
        
        # Se o tipo de agente for especificado, cria um subdiretório
        if agent_type:
            task_dir = os.path.join(task_dir, agent_type)
            os.makedirs(task_dir, exist_ok=True)
        
        # Adiciona timestamp ao nome do arquivo para evitar sobrescritas
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_with_timestamp = f"{os.path.splitext(filename)[0]}_{timestamp}{os.path.splitext(filename)[1]}"
        
        file_path = os.path.join(task_dir, filename_with_timestamp)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    def save_json(self, task_id, filename, data, agent_type=None):
        """
        Salva dados em formato JSON.
        
        Args:
            task_id (int): ID da tarefa
            filename (str): Nome do arquivo
            data (dict): Dados a serem salvos
            agent_type (str, optional): Tipo do agente (front, back, qa)
            
        Returns:
            str: Caminho completo do arquivo salvo
        """
        task_dir = self.create_task_directory(task_id)
        
        # Se o tipo de agente for especificado, cria um subdiretório
        if agent_type:
            task_dir = os.path.join(task_dir, agent_type)
            os.makedirs(task_dir, exist_ok=True)
        
        # Adiciona timestamp ao nome do arquivo para evitar sobrescritas
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_with_timestamp = f"{os.path.splitext(filename)[0]}_{timestamp}.json"
        
        file_path = os.path.join(task_dir, filename_with_timestamp)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return file_path
    
    def read_file(self, file_path):
        """
        Lê o conteúdo de um arquivo.
        
        Args:
            file_path (str): Caminho do arquivo
            
        Returns:
            str: Conteúdo do arquivo
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def read_json(self, file_path):
        """
        Lê um arquivo JSON.
        
        Args:
            file_path (str): Caminho do arquivo
            
        Returns:
            dict: Dados do arquivo JSON
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_task_files(self, task_id, agent_type=None):
        """
        Lista todos os arquivos associados a uma tarefa.
        
        Args:
            task_id (int): ID da tarefa
            agent_type (str, optional): Tipo do agente para filtrar
            
        Returns:
            list: Lista de caminhos de arquivos
        """
        task_dir = os.path.join(self.base_path, f"task_{task_id}")
        
        if not os.path.exists(task_dir):
            return []
        
        if agent_type:
            agent_dir = os.path.join(task_dir, agent_type)
            if not os.path.exists(agent_dir):
                return []
            task_dir = agent_dir
        
        result = []
        for root, _, files in os.walk(task_dir):
            for file in files:
                result.append(os.path.join(root, file))
        
        return result
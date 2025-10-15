import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name, log_file=None, level=logging.INFO):
    """
    Configura e retorna um logger com o nome especificado.
    
    Args:
        name (str): Nome do logger
        log_file (str, optional): Caminho para o arquivo de log. Se None, usa apenas console.
        level (int, optional): Nível de logging. Padrão é INFO.
        
    Returns:
        logging.Logger: O logger configurado
    """
    # Criar logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Definir formato
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Adicionar handler de console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Adicionar handler de arquivo se especificado
    if log_file:
        # Garantir que o diretório existe
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Configurar handler de arquivo rotativo (10MB, máximo 5 arquivos)
        file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
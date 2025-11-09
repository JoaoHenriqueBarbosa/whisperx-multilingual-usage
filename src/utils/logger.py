"""
Configurador de Logging
"""
import os
import sys
import logging
import warnings
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    console: bool = True,
    log_format: Optional[str] = None
):
    """
    Configura sistema de logging

    Args:
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR)
        log_file: Caminho para arquivo de log
        console: Se deve logar no console
        log_format: Formato customizado de log
    """
    # Suprimir warnings de bibliotecas externas
    _suppress_external_warnings()

    # Configurar PyTorch/CUDA otimizações
    _configure_torch()

    # Formato de log
    if not log_format:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Nível de logging
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remover handlers existentes
    root_logger.handlers.clear()

    # Handler para console
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(log_format))
        root_logger.addHandler(console_handler)

    # Handler para arquivo
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(log_format))
        root_logger.addHandler(file_handler)

    # Configurar loggers de bibliotecas externas
    _configure_external_loggers()

    logging.info("Sistema de logging configurado")


def _suppress_external_warnings():
    """Suprime warnings de bibliotecas externas"""
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", message=".*torchaudio.*")
    warnings.filterwarnings("ignore", message=".*torch.*")
    warnings.filterwarnings("ignore", message=".*pyannote.*")


def _configure_torch():
    """Configura otimizações do PyTorch"""
    try:
        import torch

        if torch.cuda.is_available():
            # Habilitar TF32 para melhor performance
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            torch.backends.cudnn.benchmark = True
    except ImportError:
        pass


def _configure_external_loggers():
    """Configura loggers de bibliotecas externas"""
    external_loggers = [
        'lightning',
        'pytorch_lightning',
        'lightning_fabric',
        'pyannote',
        'speechbrain',
        'transformers',
        'whisperx'
    ]

    for logger_name in external_loggers:
        logging.getLogger(logger_name).setLevel(logging.ERROR)

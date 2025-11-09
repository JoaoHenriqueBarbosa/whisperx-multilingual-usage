#!/usr/bin/env python3
"""
Sistema de Transcrição de Áudio - Meditations
Pipeline modular para transcrição de arquivos de áudio usando WhisperX
"""
import sys
import argparse
from pathlib import Path

from src.config import Config
from src.utils import setup_logging
from src.pipeline import TranscriptionPipeline


def parse_args():
    """Parse argumentos de linha de comando"""
    parser = argparse.ArgumentParser(
        description='Pipeline de Transcrição de Áudio',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Usar configuração padrão
  python main.py

  # Especificar arquivo de configuração customizado
  python main.py --config custom_config.yaml

  # Alterar nível de log
  python main.py --log-level DEBUG

  # Especificar diretórios manualmente
  python main.py --input data/input --output data/output
        """
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Caminho para arquivo de configuração YAML (padrão: config.yaml)'
    )

    parser.add_argument(
        '--input',
        type=str,
        help='Diretório de entrada (sobrescreve config)'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Diretório de saída (sobrescreve config)'
    )

    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Nível de logging (sobrescreve config)'
    )

    parser.add_argument(
        '--device',
        type=str,
        choices=['cuda', 'cpu', 'auto'],
        help='Dispositivo de processamento (sobrescreve config)'
    )

    parser.add_argument(
        '--model',
        type=str,
        choices=['tiny', 'base', 'small', 'medium', 'large-v2', 'large-v3'],
        help='Modelo Whisper a usar (sobrescreve config)'
    )

    return parser.parse_args()


def main():
    """Função principal"""
    # Parse argumentos
    args = parse_args()

    # Carregar configuração
    try:
        config = Config(args.config)
    except FileNotFoundError as e:
        print(f"Erro: {e}")
        print(f"Crie um arquivo de configuração em '{args.config}' ou especifique um existente com --config")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao carregar configuração: {e}")
        sys.exit(1)

    # Sobrescrever configurações com argumentos de linha de comando
    if args.input:
        config._config['paths']['input'] = args.input
    if args.output:
        config._config['paths']['output'] = args.output
    if args.device:
        config._config['device']['type'] = args.device
    if args.model:
        config._config['whisper']['model_size'] = args.model

    # Configurar logging
    log_level = args.log_level or config.get('logging.level', 'INFO')
    log_file = config.logs_path / config.get('logging.file', 'transcription.log')

    setup_logging(
        level=log_level,
        log_file=log_file,
        console=config.get('logging.console', True),
        log_format=config.get('logging.format')
    )

    # Executar pipeline
    try:
        pipeline = TranscriptionPipeline(config)
        pipeline.run()

    except KeyboardInterrupt:
        print("\n\nProcessamento interrompido pelo usuário")
        sys.exit(0)

    except Exception as e:
        print(f"\n\nErro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

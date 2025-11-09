"""
Gerenciador de Configuração
"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict
from dotenv import load_dotenv


class Config:
    """Classe para gerenciar configurações do projeto"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Inicializa configuração

        Args:
            config_path: Caminho para arquivo YAML de configuração
        """
        self.config_path = Path(config_path)
        self._config = self._load_config()
        self._load_env()

    def _load_config(self) -> Dict[str, Any]:
        """Carrega configuração do arquivo YAML"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _load_env(self):
        """Carrega variáveis de ambiente"""
        load_dotenv()
        self.hf_token = os.getenv("HF_TOKEN")

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Obtém valor de configuração usando notação de ponto

        Args:
            key_path: Caminho da chave (ex: 'whisper.model_size')
            default: Valor padrão se chave não existir

        Returns:
            Valor da configuração
        """
        keys = key_path.split('.')
        value = self._config

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default

            if value is None:
                return default

        return value

    def __getitem__(self, key: str) -> Any:
        """Permite acesso via config['key']"""
        return self._config[key]

    def __contains__(self, key: str) -> bool:
        """Permite usar 'in' para verificar existência de chave"""
        return key in self._config

    @property
    def device_type(self) -> str:
        """Tipo de dispositivo (cuda/cpu)"""
        return self.get('device.type', 'cuda')

    @property
    def compute_type(self) -> str:
        """Tipo de computação (float16/int8)"""
        return self.get('device.compute_type', 'float16')

    @property
    def whisper_model(self) -> str:
        """Modelo Whisper a usar"""
        return self.get('whisper.model_size', 'large-v2')

    @property
    def language(self) -> str:
        """Idioma para transcrição"""
        return self.get('whisper.language', 'pt')

    @property
    def batch_size(self) -> int:
        """Tamanho do batch"""
        return self.get('whisper.batch_size', 16)

    @property
    def input_path(self) -> Path:
        """Diretório de entrada"""
        return Path(self.get('paths.input', 'data/input'))

    @property
    def output_path(self) -> Path:
        """Diretório de saída"""
        return Path(self.get('paths.output', 'data/output'))

    @property
    def logs_path(self) -> Path:
        """Diretório de logs"""
        return Path(self.get('paths.logs', 'logs'))

    @property
    def audio_extensions(self) -> list:
        """Extensões de áudio suportadas"""
        return self.get('processing.audio_extensions', ['.mp3', '.wav'])

    @property
    def output_formats(self) -> list:
        """Formatos de saída"""
        return self.get('output.formats', ['json', 'txt', 'srt'])

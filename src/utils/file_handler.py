"""
Gerenciador de Arquivos
"""
import whisperx
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class FileHandler:
    """Classe para gerenciar arquivos de áudio"""

    def __init__(self, input_dir: Path, output_dir: Path, audio_extensions: List[str]):
        """
        Inicializa gerenciador de arquivos

        Args:
            input_dir: Diretório de entrada
            output_dir: Diretório de saída
            audio_extensions: Extensões de áudio suportadas
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.audio_extensions = [ext.lower() for ext in audio_extensions]

        # Criar diretórios se não existirem
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def find_audio_files(self) -> List[Path]:
        """
        Encontra todos os arquivos de áudio no diretório de entrada

        Returns:
            Lista de caminhos de arquivos de áudio
        """
        audio_files = []

        for ext in self.audio_extensions:
            audio_files.extend(self.input_dir.glob(f"*{ext}"))

        audio_files.sort()

        if audio_files:
            logger.info(f"Encontrados {len(audio_files)} arquivo(s) de áudio")
            for f in audio_files:
                size_mb = f.stat().st_size / 1024 / 1024
                logger.info(f"  - {f.name} ({size_mb:.2f} MB)")
        else:
            logger.warning(f"Nenhum arquivo de áudio encontrado em {self.input_dir}")

        return audio_files

    def load_audio(self, audio_path: Path) -> any:
        """
        Carrega arquivo de áudio

        Args:
            audio_path: Caminho do arquivo

        Returns:
            Dados de áudio carregados
        """
        logger.info(f"Carregando áudio: {audio_path.name}")
        return whisperx.load_audio(str(audio_path))

    def get_output_path(self, audio_path: Path, extension: str) -> Path:
        """
        Gera caminho de saída para arquivo

        Args:
            audio_path: Caminho do arquivo de áudio original
            extension: Extensão do arquivo de saída

        Returns:
            Caminho completo do arquivo de saída
        """
        base_name = audio_path.stem
        return self.output_dir / f"{base_name}_transcricao.{extension}"

    def output_exists(self, audio_path: Path, formats: List[str]) -> bool:
        """
        Verifica se saída já existe

        Args:
            audio_path: Caminho do arquivo de áudio
            formats: Formatos a verificar

        Returns:
            True se todos os formatos existem
        """
        return all(
            self.get_output_path(audio_path, fmt).exists()
            for fmt in formats
        )

"""
Pipeline de Transcrição de Áudio
"""
import whisperx
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..config import Config
from ..models import ModelLoader
from ..utils import FileHandler, Exporter

logger = logging.getLogger(__name__)


class TranscriptionPipeline:
    """Pipeline completo de transcrição de áudio"""

    def __init__(self, config: Config):
        """
        Inicializa pipeline

        Args:
            config: Configuração do sistema
        """
        self.config = config

        # Inicializar componentes
        self.model_loader = ModelLoader(
            device=config.device_type,
            compute_type=config.compute_type
        )

        self.file_handler = FileHandler(
            input_dir=config.input_path,
            output_dir=config.output_path,
            audio_extensions=config.audio_extensions
        )

        self.exporter = Exporter(config.get('output', {}))

        # Estado
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }

    def run(self):
        """Executa pipeline completo"""
        logger.info("="*60)
        logger.info("Iniciando Pipeline de Transcrição")
        logger.info("="*60)

        # Carregar modelo Whisper
        self.model_loader.load_whisper_model(
            model_size=self.config.whisper_model,
            language=self.config.language
        )

        # Encontrar arquivos
        audio_files = self.file_handler.find_audio_files()

        if not audio_files:
            logger.warning("Nenhum arquivo para processar")
            return

        self.stats['total'] = len(audio_files)

        # Processar cada arquivo
        for audio_file in audio_files:
            try:
                self._process_file(audio_file)
                self.stats['success'] += 1
            except Exception as e:
                logger.error(f"Erro ao processar {audio_file.name}: {e}", exc_info=True)
                self.stats['failed'] += 1

        # Cleanup
        self.model_loader.cleanup()

        # Estatísticas finais
        self._print_stats()

    def _process_file(self, audio_path: Path):
        """
        Processa um arquivo de áudio

        Args:
            audio_path: Caminho do arquivo
        """
        logger.info("="*60)
        logger.info(f"Processando: {audio_path.name}")
        logger.info("="*60)

        # Verificar se já existe
        if self.config.get('processing.skip_existing', False):
            if self.file_handler.output_exists(audio_path, self.config.output_formats):
                logger.info(f"Saída já existe, pulando: {audio_path.name}")
                self.stats['skipped'] += 1
                return

        # 1. Carregar áudio
        audio = self.file_handler.load_audio(audio_path)

        # 2. Transcrever
        result = self._transcribe(audio)

        # 3. Alinhar
        if self.config.get('alignment.enabled', True):
            result = self._align(audio, result)

        # 4. Diarização (opcional)
        if self.config.get('diarization.enabled', False):
            result = self._diarize(audio_path, result)

        # 5. Exportar resultados
        output_base = self.file_handler.get_output_path(audio_path, '')
        self.exporter.export(
            result=result,
            output_path=output_base,
            formats=self.config.output_formats
        )

        logger.info(f"Transcrição concluída: {audio_path.name}")

    def _transcribe(self, audio: Any) -> Dict[str, Any]:
        """
        Transcreve áudio

        Args:
            audio: Dados de áudio

        Returns:
            Resultado da transcrição
        """
        logger.info("Transcrevendo áudio...")

        model = self.model_loader.get_whisper_model()
        result = model.transcribe(
            audio,
            batch_size=self.config.batch_size
        )

        num_segments = len(result.get('segments', []))
        logger.info(f"Transcrição concluída: {num_segments} segmentos")

        return result

    def _align(self, audio: Any, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Alinha transcrição com timestamps precisos

        Args:
            audio: Dados de áudio
            result: Resultado da transcrição

        Returns:
            Resultado alinhado
        """
        logger.info("Alinhando transcrição...")

        # Carregar modelo de alinhamento
        align_model, metadata = self.model_loader.load_alignment_model(
            language_code=result.get("language", self.config.language)
        )

        # Alinhar
        result = whisperx.align(
            result["segments"],
            align_model,
            metadata,
            audio,
            self.model_loader.device,
            return_char_alignments=self.config.get('alignment.return_char_alignments', False)
        )

        logger.info("Alinhamento concluído")

        return result

    def _diarize(self, audio_path: Path, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza diarização (identificação de speakers)

        Args:
            audio_path: Caminho do arquivo de áudio
            result: Resultado da transcrição

        Returns:
            Resultado com speakers identificados
        """
        try:
            logger.info("Realizando diarização...")

            diarize_model = self.model_loader.load_diarization_model(
                hf_token=self.config.hf_token
            )

            # Processar áudio
            diarize_segments = diarize_model(str(audio_path))

            # Atribuir speakers
            result = whisperx.assign_word_speakers(diarize_segments, result)

            logger.info("Diarização concluída")

        except Exception as e:
            logger.warning(f"Erro na diarização: {e}")
            logger.info("Continuando sem identificação de speakers...")

        return result

    def _print_stats(self):
        """Imprime estatísticas finais"""
        logger.info("="*60)
        logger.info("Estatísticas Finais")
        logger.info("="*60)
        logger.info(f"Total de arquivos: {self.stats['total']}")
        logger.info(f"Sucesso: {self.stats['success']}")
        logger.info(f"Falhas: {self.stats['failed']}")
        logger.info(f"Pulados: {self.stats['skipped']}")
        logger.info("="*60)

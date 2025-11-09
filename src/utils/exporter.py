"""
Exportador de Resultados
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class Exporter:
    """Classe para exportar resultados de transcrição"""

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa exportador

        Args:
            config: Configuração de saída
        """
        self.config = config

    def export(
        self,
        result: Dict[str, Any],
        output_path: Path,
        formats: List[str]
    ) -> List[Path]:
        """
        Exporta resultado em múltiplos formatos

        Args:
            result: Resultado da transcrição
            output_path: Caminho base para saída
            formats: Formatos a exportar

        Returns:
            Lista de caminhos dos arquivos gerados
        """
        exported_files = []

        for fmt in formats:
            try:
                if fmt == 'json':
                    path = self.export_json(result, output_path)
                elif fmt == 'txt':
                    path = self.export_txt(result, output_path)
                elif fmt == 'srt':
                    path = self.export_srt(result, output_path)
                else:
                    logger.warning(f"Formato desconhecido: {fmt}")
                    continue

                exported_files.append(path)
                logger.info(f"Exportado: {path.name}")

            except Exception as e:
                logger.error(f"Erro ao exportar {fmt}: {e}")

        return exported_files

    def export_json(self, result: Dict[str, Any], base_path: Path) -> Path:
        """
        Exporta como JSON

        Args:
            result: Resultado da transcrição
            base_path: Caminho base

        Returns:
            Caminho do arquivo JSON
        """
        json_path = base_path.parent / f"{base_path.stem}.json"

        json_config = self.config.get('json', {})

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(
                result,
                f,
                ensure_ascii=json_config.get('ensure_ascii', False),
                indent=json_config.get('indent', 2)
            )

        return json_path

    def export_txt(self, result: Dict[str, Any], base_path: Path) -> Path:
        """
        Exporta como TXT

        Args:
            result: Resultado da transcrição
            base_path: Caminho base

        Returns:
            Caminho do arquivo TXT
        """
        txt_path = base_path.parent / f"{base_path.stem}.txt"

        txt_config = self.config.get('txt', {})
        include_speakers = txt_config.get('include_speakers', True)
        include_timestamps = txt_config.get('include_timestamps', False)

        with open(txt_path, 'w', encoding='utf-8') as f:
            for segment in result.get("segments", []):
                line_parts = []

                # Speaker
                if include_speakers and 'speaker' in segment:
                    line_parts.append(f"[{segment['speaker']}]")

                # Timestamp
                if include_timestamps:
                    start = self._format_timestamp(segment.get('start', 0))
                    end = self._format_timestamp(segment.get('end', 0))
                    line_parts.append(f"[{start} -> {end}]")

                # Texto
                line_parts.append(segment.get('text', '').strip())

                f.write(' '.join(line_parts) + '\n')

        return txt_path

    def export_srt(self, result: Dict[str, Any], base_path: Path) -> Path:
        """
        Exporta como SRT (legendas)

        Args:
            result: Resultado da transcrição
            base_path: Caminho base

        Returns:
            Caminho do arquivo SRT
        """
        srt_path = base_path.parent / f"{base_path.stem}.srt"

        with open(srt_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result.get("segments", []), 1):
                start = segment.get('start', 0)
                end = segment.get('end', 0)
                text = segment.get('text', '').strip()

                # Converter para formato SRT (HH:MM:SS,mmm)
                start_time = self._to_srt_time(start)
                end_time = self._to_srt_time(end)

                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")

        return srt_path

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Formata timestamp em MM:SS"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"

    @staticmethod
    def _to_srt_time(seconds: float) -> str:
        """Converte segundos para formato SRT"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

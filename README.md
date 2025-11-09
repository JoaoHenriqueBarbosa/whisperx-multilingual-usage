# Sistema de Transcrição de Áudio - Meditations

Pipeline modular profissional para transcrição de arquivos de áudio usando WhisperX e PyTorch.

## Características

- **Pipeline Modular**: Arquitetura limpa e extensível seguindo padrões da indústria
- **Alto Performance**: Otimizado para GPUs NVIDIA com suporte a TF32 e cuDNN
- **Múltiplos Formatos**: Exporta em JSON, TXT e SRT (legendas)
- **Configurável**: Sistema de configuração centralizado via YAML
- **Logging Avançado**: Sistema de logs completo com níveis configuráveis
- **Alinhamento Preciso**: Timestamps em nível de palavra usando alignment models
- **Diarização (Opcional)**: Identificação de diferentes speakers

## Estrutura do Projeto

```
meditations/
├── config.yaml              # Configuração principal
├── main.py                  # Script principal
├── run.sh                   # Script de execução
├── requirements.txt         # Dependências Python
├── .env                     # Variáveis de ambiente (HF_TOKEN)
│
├── src/
│   ├── config/             # Módulo de configuração
│   │   └── config_loader.py
│   ├── models/             # Gerenciamento de modelos ML
│   │   └── model_loader.py
│   ├── pipeline/           # Pipeline de processamento
│   │   └── transcription_pipeline.py
│   └── utils/              # Utilitários
│       ├── file_handler.py
│       ├── exporter.py
│       └── logger.py
│
├── data/
│   ├── input/              # Arquivos de áudio para processar
│   └── output/             # Transcrições geradas
│
└── logs/                    # Arquivos de log
```

## Instalação

### Pré-requisitos

- Python 3.12+
- CUDA 12+ (para GPU)
- FFmpeg

### Passos

1. **Clone e configure o ambiente**:
```bash
cd /path/to/project
python3 -m venv venv
source venv/bin/activate
```

2. **Instale dependências**:
```bash
pip install -r requirements.txt
```

3. **Configure variáveis de ambiente**:
```bash
# Crie arquivo .env
echo "HF_TOKEN=seu_token_aqui" > .env
```

## Configuração

Edite `config.yaml` para customizar o comportamento:

```yaml
# Dispositivo
device:
  type: "cuda"  # cuda, cpu, auto
  compute_type: "float16"

# Modelo Whisper
whisper:
  model_size: "large-v2"  # tiny, base, small, medium, large-v2, large-v3
  language: "pt"
  batch_size: 16

# Formatos de saída
output:
  formats:
    - json
    - txt
    - srt
```

## Uso

### Uso Básico

1. Coloque seus arquivos de áudio em `data/input/`
2. Execute:
```bash
./run.sh
```

3. Encontre as transcrições em `data/output/`

### Opções de Linha de Comando

```bash
# Usar configuração customizada
./run.sh --config custom_config.yaml

# Alterar modelo
./run.sh --model base

# Alterar dispositivo
./run.sh --device cpu

# Modo debug
./run.sh --log-level DEBUG

# Especificar diretórios
./run.sh --input /path/to/audio --output /path/to/output

# Ver todas as opções
python main.py --help
```

### Uso Programático

```python
from src.config import Config
from src.pipeline import TranscriptionPipeline
from src.utils import setup_logging

# Configurar
config = Config("config.yaml")
setup_logging(level="INFO")

# Executar pipeline
pipeline = TranscriptionPipeline(config)
pipeline.run()
```

## Formatos de Saída

### JSON
Contém todos os metadados, timestamps e informações de alinhamento:
```json
{
  "segments": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": " Olá e bem-vindo...",
      "words": [...]
    }
  ]
}
```

### TXT
Texto puro, fácil de ler:
```
Olá e bem-vindo ao nosso terceiro dia de prática.
Talvez você tenha notado que à medida que nós vamos praticando...
```

### SRT (Legendas)
Formato padrão de legendas:
```
1
00:00:00,000 --> 00:00:02,500
Olá e bem-vindo ao nosso terceiro dia de prática.

2
00:00:02,500 --> 00:00:05,000
Talvez você tenha notado...
```

## Modelos Disponíveis

| Modelo | Tamanho | VRAM | Velocidade | Qualidade |
|--------|---------|------|------------|-----------|
| tiny | ~39M | ~1GB | Muito Rápido | Básica |
| base | ~74M | ~1GB | Rápido | Boa |
| small | ~244M | ~2GB | Médio | Muito Boa |
| medium | ~769M | ~5GB | Lento | Excelente |
| large-v2 | ~1550M | ~10GB | Muito Lento | Superior |
| large-v3 | ~1550M | ~10GB | Muito Lento | Superior+ |

## Performance

Com GPU NVIDIA RTX 5060 Ti (8GB):
- **Modelo large-v2**: ~6 segundos para 13MB de áudio (~2min de fala)
- **Alinhamento**: ~30 segundos adicionais
- **Total**: ~40-50 segundos por arquivo

## Troubleshooting

### Erro: CUDA out of memory
- Reduza `batch_size` em `config.yaml`
- Use modelo menor (ex: `medium` em vez de `large-v2`)

### Erro: FFmpeg não encontrado
```bash
sudo apt-get install ffmpeg
```

### Erro: cuDNN não encontrado
O script `run.sh` já configura `LD_LIBRARY_PATH` automaticamente.

## Diarização (Opcional)

Para habilitar identificação de speakers:

1. Acesse https://hf.co/pyannote/speaker-diarization-3.1 e aceite os termos
2. Em `config.yaml`:
```yaml
diarization:
  enabled: true
```

## Desenvolvimento

### Adicionar Novo Formato de Exportação

Edite `src/utils/exporter.py`:
```python
def export_custom(self, result: Dict, base_path: Path) -> Path:
    # Sua lógica aqui
    pass
```

### Adicionar Novo Step na Pipeline

Edite `src/pipeline/transcription_pipeline.py`:
```python
def _process_file(self, audio_path: Path):
    # ... passos existentes
    result = self._custom_step(result)
    # ...
```

## Logging

Logs são salvos em:
- Console: Saída formatada em tempo real
- Arquivo: `logs/transcription.log` (configurável)

Níveis disponíveis: DEBUG, INFO, WARNING, ERROR

## Licença

MIT

## Contribuindo

Pull requests são bem-vindos. Para mudanças maiores, abra uma issue primeiro.

## Suporte

Para bugs e solicitações de features, abra uma issue no repositório.

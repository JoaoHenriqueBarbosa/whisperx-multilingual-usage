# Arquitetura do Sistema

## Visão Geral

Sistema modular de transcrição de áudio baseado em pipeline, seguindo princípios de Clean Architecture e SOLID.

## Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                              │
│                   (Entry Point / CLI)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  TranscriptionPipeline                       │
│              (Orquestração do Fluxo)                         │
└─┬──────────┬──────────┬──────────┬────────────┬─────────────┘
  │          │          │          │            │
  ▼          ▼          ▼          ▼            ▼
┌────┐   ┌────────┐ ┌────────┐ ┌─────────┐ ┌─────────┐
│Cfg │   │ Model  │ │  File  │ │Exporter │ │ Logger  │
│    │   │ Loader │ │Handler │ │         │ │         │
└────┘   └────────┘ └────────┘ └─────────┘ └─────────┘
```

## Módulos

### 1. Config (`src/config/`)

**Responsabilidade**: Gerenciar configurações do sistema

**Componentes**:
- `config_loader.py`: Carrega e valida YAML de configuração

**Características**:
- Carregamento de YAML
- Validação de configurações
- Acesso via propriedades
- Suporte a variáveis de ambiente (.env)

### 2. Models (`src/models/`)

**Responsabilidade**: Gerenciar modelos de Machine Learning

**Componentes**:
- `model_loader.py`: Carrega modelos Whisper, Alignment e Diarization

**Características**:
- Lazy loading de modelos
- Gerenciamento de memória GPU
- Cache de modelos carregados
- Detecção automática de dispositivo (CUDA/CPU)

### 3. Pipeline (`src/pipeline/`)

**Responsabilidade**: Orquestrar o fluxo de processamento

**Componentes**:
- `transcription_pipeline.py`: Pipeline principal de transcrição

**Fluxo de Processamento**:
```
1. Load Audio
    ↓
2. Transcribe (Whisper)
    ↓
3. Align (Word-level timestamps)
    ↓
4. Diarize (Speaker identification) [opcional]
    ↓
5. Export (JSON/TXT/SRT)
```

### 4. Utils (`src/utils/`)

**Responsabilidade**: Funcionalidades auxiliares

**Componentes**:
- `file_handler.py`: Gerenciamento de arquivos I/O
- `exporter.py`: Exportação em múltiplos formatos
- `logger.py`: Configuração de logging

**Características**:
- Descoberta automática de arquivos
- Exportação plugável (fácil adicionar formatos)
- Logging estruturado com níveis

## Fluxo de Dados

```
Audio File (MP3/WAV/etc)
    ↓
[FileHandler] → Load & Validate
    ↓
[ModelLoader] → Whisper Model
    ↓
[Pipeline] → Transcription
    ↓
Raw Segments {text, timestamps}
    ↓
[ModelLoader] → Alignment Model
    ↓
[Pipeline] → Precise Alignment
    ↓
Aligned Segments {text, word_timestamps}
    ↓
[Exporter] → JSON/TXT/SRT
    ↓
Output Files
```

## Padrões de Design

### 1. Pipeline Pattern
O `TranscriptionPipeline` implementa o padrão Pipeline, onde cada step processa e passa dados para o próximo.

### 2. Strategy Pattern
O `Exporter` usa Strategy para diferentes formatos de exportação (JSON, TXT, SRT).

### 3. Facade Pattern
O `ModelLoader` fornece interface simplificada para gerenciar múltiplos modelos complexos.

### 4. Dependency Injection
Componentes recebem dependências via construtor (ex: Pipeline recebe Config).

## Princípios SOLID

### Single Responsibility
- `FileHandler`: apenas I/O de arquivos
- `Exporter`: apenas exportação
- `ModelLoader`: apenas gerenciamento de modelos

### Open/Closed
- Fácil adicionar novos formatos de exportação sem modificar código existente
- Extensível via herança e composição

### Liskov Substitution
- Componentes podem ser substituídos por mock objects para testes

### Interface Segregation
- Interfaces pequenas e focadas (Config properties)

### Dependency Inversion
- Pipeline depende de abstrações (Config) não de implementações concretas

## Configuração

### Hierarquia de Configuração

```
1. config.yaml (base)
    ↓
2. .env (secrets)
    ↓
3. CLI args (override)
    ↓
Configuração Final
```

### Exemplo de Fluxo

```yaml
# config.yaml
device:
  type: "cuda"
whisper:
  model_size: "large-v2"
```

```bash
# Override via CLI
./run.sh --model base --device cpu
```

Resultado: `base` em `cpu` (CLI override config)

## Extensibilidade

### Adicionar Novo Formato de Saída

1. Adicionar método em `Exporter`:
```python
def export_vtt(self, result, base_path):
    # Implementação
    pass
```

2. Registrar em `export()`:
```python
if fmt == 'vtt':
    path = self.export_vtt(result, output_path)
```

3. Adicionar em `config.yaml`:
```yaml
output:
  formats:
    - vtt
```

### Adicionar Novo Step na Pipeline

1. Criar método privado em `TranscriptionPipeline`:
```python
def _custom_processing(self, result):
    # Lógica
    return result
```

2. Adicionar no fluxo `_process_file()`:
```python
result = self._custom_processing(result)
```

### Adicionar Novo Modelo

1. Adicionar método em `ModelLoader`:
```python
def load_custom_model(self):
    # Carregamento
    return model
```

2. Usar na pipeline conforme necessário

## Performance

### Otimizações Implementadas

1. **GPU Acceleration**
   - TF32 habilitado
   - cuDNN benchmark mode
   - Batch processing

2. **Memory Management**
   - Cleanup explícito de modelos
   - CUDA cache clearing
   - Lazy loading

3. **I/O Optimization**
   - Skip existing files (opcional)
   - Batch file discovery

### Bottlenecks Conhecidos

1. **Model Loading**: ~10-15s inicial
   - Mitigação: Carregar uma vez, processar múltiplos arquivos

2. **Alignment**: ~30s por arquivo
   - Mitigação: Desabilitar se não precisar de timestamps precisos

3. **Diarization**: ~60-120s por arquivo
   - Mitigação: Desabilitar se não precisar de speaker identification

## Logging

### Níveis de Log

- **DEBUG**: Informações detalhadas para debugging
- **INFO**: Confirmações de operações normais
- **WARNING**: Avisos que não param execução
- **ERROR**: Erros que impedem operação específica

### Saídas

- Console: Logs formatados em tempo real
- Arquivo: `logs/transcription.log` (rotação manual)

## Testing Strategy (Futuro)

### Unit Tests
```
tests/
├── test_config.py
├── test_model_loader.py
├── test_file_handler.py
├── test_exporter.py
└── test_pipeline.py
```

### Integration Tests
- Test completo end-to-end
- Mock de modelos pesados

### Performance Tests
- Benchmark de diferentes modelos
- Profiling de memória GPU

## Deployment

### Local
```bash
./run.sh
```

### Docker (Futuro)
```dockerfile
FROM nvidia/cuda:12.0-runtime
# Setup environment
# Run pipeline
```

### Cloud (Futuro)
- AWS Lambda (com GPU)
- Google Cloud Run
- Azure Container Instances

## Manutenção

### Atualização de Dependências

```bash
pip list --outdated
pip install -U whisperx torch
```

### Backup de Modelos

Modelos são baixados em `~/.cache/huggingface/`
```bash
# Backup
tar -czf models_backup.tar.gz ~/.cache/huggingface/

# Restore
tar -xzf models_backup.tar.gz -C ~/
```

## Segurança

### Secrets Management
- `.env` para tokens (não commitar)
- `.gitignore` configurado
- Variáveis de ambiente no runtime

### Input Validation
- Validação de extensões de arquivo
- Verificação de tamanhos
- Sanitização de paths

## Roadmap

### v1.1
- [ ] Suporte a processamento em batch paralelo
- [ ] Web UI para upload e download
- [ ] API REST

### v1.2
- [ ] Suporte a mais idiomas automaticamente
- [ ] Auto-detection de idioma
- [ ] Streaming de áudio longo

### v2.0
- [ ] Fine-tuning de modelos
- [ ] Custom vocabulary
- [ ] Real-time transcription

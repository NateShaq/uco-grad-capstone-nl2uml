# nl2uml Flask Backend

This backend powers diagram generation/refinement and code conversion. It can run against local Ollama models or external providers.

## Ollama multi-model pipeline

We support a chained Ollama flow (reasoning → PlantUML → validation) using these models:

- `deepseek-coder-v2:latest` (reasoning JSON IR)
- `llama3.1:70b` (reasoning JSON IR, alternate)
- `qwen2.5-coder:7b` (PlantUML)
- `codellama:7b` (PlantUML alternate)
- `magicoder:latest` (validation fallback)

### Install models on the host

```bash
ollama pull deepseek-coder-v2:latest
ollama pull llama3.1:70b
ollama pull qwen2.5-coder:7b
ollama pull codellama:7b
ollama pull magicoder:latest
ollama serve   # starts http://localhost:11434
```

The Docker backend calls the host Ollama runtime at `http://host.docker.internal:11434`, so no install is needed inside the container—just pull on the host where `ollama serve` runs.

### Configure docker-compose

`docker-compose.yml` already exposes these env vars:

- `AI_AGENT_TYPE=ollama-pipeline` (set to make the chain the default)
- `OLLAMA_IDEATION_MODELS="deepseek-coder-v2:latest, llama3.1:70b"`
- `OLLAMA_UML_MODELS="qwen2.5-coder:7b, deepseek-coder-v2:latest, codellama:7b, llama3.1:70b"`
- `OLLAMA_VALIDATION_MODELS="magicoder:latest, codellama:7b"`
- `OLLAMA_HOST=http://host.docker.internal:11434`

### Optional debug logging

Set `OLLAMA_PIPELINE_DEBUG=1` to log each stage’s output preview in the backend.

### Toggle PlantUML sanitizer

By default, class diagrams run through a sanitizer to strip bad tokens. To temporarily disable it (e.g., to inspect raw model output), set:

```bash
ENABLE_PLANTUML_SANITIZER=0
```


# Run with Ollama backend

1) Install Ollama on your host and pull the models used by the pipeline:
   ```bash
   brew install --cask ollama
   # ideation / reasoning stage (stage 1)
   ollama pull deepseek-coder-v2:latest
   ollama pull llama3.1:70b

   # PlantUML generation stage (stage 2)
   ollama pull qwen2.5-coder:7b
   ollama pull codellama:7b

   # validator / fixer (stage 3, optional)
   ollama pull magicoder:latest

   ollama serve   # starts http://localhost:11434
   ```

2) Start the Flask container pointing at Ollama:
   ```bash
   export OLLAMA_HOST=http://host.docker.internal:11434
   export OLLAMA_MODEL=mistral
   export AGENT_BACKEND=ollama
   docker run --rm -p 8080:8080 \
     -e OLLAMA_HOST=$OLLAMA_HOST -e OLLAMA_MODEL=$OLLAMA_MODEL -e AGENT_BACKEND=$AGENT_BACKEND \
     -e OLLAMA_IDEATION_MODELS="deepseek-coder-v2:latest, llama3.1:70b" \
     -e OLLAMA_UML_MODELS="qwen2.5-coder:7b, deepseek-coder-v2:latest, codellama:7b, llama3.1:70b" \
     -e OLLAMA_VALIDATION_MODELS="magicoder:latest, codellama:7b" \
     -v "$PWD/data":/var/lib/nl2uml nl2uml:local
   ```

3) To switch to the multi-model chain from the UI, choose the "Ollama Pipeline" agent. You can also set `AI_AGENT_TYPE=ollama-pipeline` in `docker-compose.yml` to make it the backend default.

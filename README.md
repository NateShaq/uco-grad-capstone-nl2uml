# NL2UML Graduate Project

Two containerized apps:
- `nl2uml-flask-backend-main`: Flask API that turns natural language into UML using Ollama-hosted models.
- `nl2uml-frontend-main`: React UI that connects to the backend.

## Requirements
- Docker + Docker Compose
- Ports `8080` (API) and `3001` (UI) available on the host
- Ollama running on the host when using the default AI agent (`AI_AGENT_TYPE=ollama`)
  - Suggested quick start: `brew install --cask ollama && ollama pull mistral && ollama serve`

### Ollama checks and models
- Is Ollama running? `curl -sf http://localhost:11434/api/version` (JSON returns version if the daemon is up).
- What models are available? `ollama list`
- Start the daemon manually (if not already running): `ollama serve`
- Pull recommended models:
  - Single-model (default): `ollama pull mistral`
  - Pipeline (set `AI_AGENT_TYPE=ollama-pipeline`): `ollama pull deepseek-coder-v2:latest llama3.1:70b llama3-code:latest codellama:7b`

## Quick start (fresh clone)
1) Clone the repo and move into it:
   ```bash
   git clone <your repo url> nl2uml
   cd nl2uml
   ```
2) (If using Ollama) ensure the host runtime is up and listening on `http://localhost:11434` and that the model named in `OLLAMA_MODEL` is pulled (default `mistral`).
3) Build and start both services:
   ```bash
   docker compose up --build
   ```
4) Open the app at http://localhost:3001 (backend health check: http://localhost:8080/health).

Stop the stack with `docker compose down`. Data written by the backend is persisted to `./data` on the host.

## Configuration
- Backend env vars live in `docker-compose.yml` under the `backend` service:
  - `AI_AGENT_TYPE=ollama` uses a single Ollama model named by `OLLAMA_MODEL`.
  - Set `AI_AGENT_TYPE=ollama-pipeline` to enable the multi-model chain; pull the models listed in `nl2uml-flask-backend-main/README.md`.
  - `OLLAMA_HOST` defaults to `http://host.docker.internal:11434`; update if your runtime is elsewhere.
  - `SQLITE_DB_PATH` points at `/var/lib/nl2uml/db/nl2uml.sqlite`; the host directory is `./data`.
- Frontend build args (API base URL, websockets) are also in `docker-compose.yml` under `frontend`.

## Local development without Docker
- Backend: `cd nl2uml-flask-backend-main && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && FLASK_APP=app:create_app FLASK_RUN_PORT=8080 flask run` (set env vars from `.env.sample` as needed).
- Frontend: `cd nl2uml-frontend-main && npm install && REACT_APP_API_BASE=http://localhost:8080 npm start` (CRA dev server on port 3000).

## Useful Docker maintenance commands
If you run into flaky containers or cached layers, these commands help reset the stack:
```bash
docker compose down -v --remove-orphans
docker builder prune -af
docker compose build --no-cache
docker compose up -d
docker logs -f nl2uml-backend
```
- Scope: these commands target this Compose project. To avoid collisions on shared hosts, set a unique project name before running them:
  ```bash
  export COMPOSE_PROJECT_NAME=nate-nl2uml   # or any unique name
  ```
  Note: `docker builder prune -af` is global build cache cleanup; skip it if others are building images on the same host.

## Repository layout
- `docker-compose.yml` – builds/runs the full stack.
- `nl2uml-flask-backend-main/` – Flask API, PlantUML tooling, model configuration docs.
- `nl2uml-frontend-main/` – React UI (Create React App).
- `data/` – host-persisted SQLite databases and uploads (ignored by git).

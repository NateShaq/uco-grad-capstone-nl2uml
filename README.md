# NL2UML Graduate Project

Two containerized apps:
- `nl2uml-flask-backend-main`: Flask API that turns natural language into UML using Ollama-hosted models.
- `nl2uml-frontend-main`: React UI that connects to the backend.

## Requirements
- Docker + Docker Compose
- Ports `8080` (API) and `3001` (UI) available on the host
- Ollama reachable by the containers at `http://host.docker.internal:11434` (the scripts below bind Ollama to `0.0.0.0:11434` so the containers can reach it)
- Java runtime available on the host (used by PlantUML inside the backend)

## Host setup scripts (recommended)
Use one of these to install prerequisites, start Ollama, pull models, and launch the stack:
- macOS: `chmod +x Install_MacOS.sh && ./Install_MacOS.sh`
- Linux (Debian/Ubuntu-like): `chmod +x Install_Linux.sh && ./Install_Linux.sh`
- Windows: run an elevated PowerShell and execute `powershell -ExecutionPolicy Bypass -File .\Install_Windows.ps1` (requires winget)

Env toggles:
- `INSTALL_ALL_MODELS=true` pulls the full pipeline set (big downloads). Default pulls only `mistral`.
- `OLLAMA_MODELS="model1 model2"` overrides the list to pull.

What the scripts do:
- Install Docker (Desktop on macOS; engine + compose plugin on Linux) and ensure the daemon is running.
- Install Ollama, bind it to `0.0.0.0:11434` with `OLLAMA_ORIGINS=*`, and start the daemon.
- Pull the requested models via `ollama pull`.
- Install OpenJDK if `java` is missing.
- Run `docker compose up --build -d` from the repo root.

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
  - `ALLOWED_ORIGINS` lets you whitelist non-localhost frontends (comma-separated).
- Frontend build args (API base URL, websockets) are also in `docker-compose.yml` under `frontend`; set `REACT_APP_API_BASE`, `REACT_APP_WS_URL`, and `REACT_APP_WS_ENABLED` there (or via `.env`) to use a DNS name instead of localhost.

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

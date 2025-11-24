# NL2UML Graduate Project

Two containerized apps:
- `nl2uml-flask-backend-main`: Flask API that turns natural language into UML using Ollama-hosted models.
- `nl2uml-frontend-main`: React UI that connects to the backend.

## Requirements
- Docker + Docker Compose
- Ports `8080` (API) and `3001` (UI) available on the host
- Ollama running on the host when using the default AI agent (`AI_AGENT_TYPE=ollama`)
  - Suggested quick start: `brew install --cask ollama && ollama pull mistral && ollama serve`

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

## Repository layout
- `docker-compose.yml` – builds/runs the full stack.
- `nl2uml-flask-backend-main/` – Flask API, PlantUML tooling, model configuration docs.
- `nl2uml-frontend-main/` – React UI (Create React App).
- `data/` – host-persisted SQLite databases and uploads (ignored by git).

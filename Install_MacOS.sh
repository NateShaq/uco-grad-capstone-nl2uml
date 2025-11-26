#!/usr/bin/env bash
set -euo pipefail

# Installs and configures Ollama, Docker Desktop, Java, pulls models, and runs docker-compose.
# Usage: INSTALL_ALL_MODELS=true ./Install_MacOS.sh
#        OLLAMA_MODELS="mistral" ./Install_MacOS.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DEFAULT_MODELS="mistral"
PIPELINE_MODELS="deepseek-coder-v2:latest gemma3:12b llama3.1:70b gemma3:27b qwen2.5-coder:7b codellama:7b gemma3:4b magicoder:latest"
if [[ "${INSTALL_ALL_MODELS:-}" == "true" ]]; then
  OLLAMA_MODELS="${PIPELINE_MODELS} ${DEFAULT_MODELS}"
else
  OLLAMA_MODELS="${OLLAMA_MODELS:-$DEFAULT_MODELS}"
fi

log() { echo "[$(date +%H:%M:%S)] $*"; }

ensure_brew() {
  if ! command -v brew >/dev/null 2>&1; then
    cat <<'EOF'
Homebrew is required but not found. Install it first:
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
Then re-run this script.
EOF
    exit 1
  fi
}

ensure_ollama() {
  if ! command -v ollama >/dev/null 2>&1; then
    log "Installing Ollama (brew cask)..."
    brew install --cask ollama
  else
    log "Ollama already installed."
  fi
}

ensure_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    log "Installing Docker Desktop (brew cask)..."
    brew install --cask docker
  else
    log "Docker already installed."
  fi

  if command -v open >/dev/null 2>&1; then
    log "Ensuring Docker Desktop is running..."
    open -g -a Docker || true
  fi

  for _ in {1..30}; do
    if docker info >/dev/null 2>&1; then
      log "Docker daemon is up."
      return
    fi
    sleep 2
  done

  log "Docker daemon did not become ready. Start Docker Desktop manually, then re-run."
  exit 1
}

ensure_java() {
  if ! command -v java >/dev/null 2>&1; then
    log "Installing OpenJDK (brew)..."
    brew install openjdk
    # Add symlink to match macOS JVM conventions if needed.
    sudo ln -sf "$(/usr/libexec/java_home)/bin/java" /usr/local/bin/java 2>/dev/null || true
  else
    log "Java already installed."
  fi
}

start_ollama_daemon() {
  if curl -sf http://localhost:11434/api/version >/dev/null 2>&1; then
    log "Ollama daemon already running."
    return
  fi

  log "Starting Ollama daemon bound to 0.0.0.0:11434..."
  OLLAMA_HOST="0.0.0.0:11434" OLLAMA_ORIGINS="*" nohup ollama serve >/tmp/ollama-serve.log 2>&1 &

  for _ in {1..20}; do
    if curl -sf http://localhost:11434/api/version >/dev/null 2>&1; then
      log "Ollama daemon is up."
      return
    fi
    sleep 2
  done

  log "Ollama daemon did not become ready; check /tmp/ollama-serve.log."
  exit 1
}

pull_models() {
  for model in ${OLLAMA_MODELS}; do
    log "Pulling model: ${model}"
    if ! ollama pull "${model}"; then
      log "Failed to pull model ${model}."
      exit 1
    fi
  done
}

detect_compose() {
  if docker compose version >/dev/null 2>&1; then
    echo "docker compose"
  elif command -v docker-compose >/dev/null 2>&1; then
    echo "docker-compose"
  else
    log "Docker Compose not found. Install Docker Desktop or docker-compose."
    exit 1
  fi
}

run_compose() {
  local compose_cmd
  compose_cmd="$(detect_compose)"
  log "Running '${compose_cmd} up --build -d' from ${ROOT_DIR}"
  (cd "${ROOT_DIR}" && ${compose_cmd} up --build -d)
}

main() {
  log "Starting macOS setup..."
  ensure_brew
  ensure_docker
  ensure_java
  ensure_ollama
  start_ollama_daemon
  pull_models
  run_compose
  log "Setup complete."
}

main "$@"

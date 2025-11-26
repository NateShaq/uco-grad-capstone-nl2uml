#!/usr/bin/env bash
set -euo pipefail

# Installs and configures Ollama, Docker, Java (OpenJDK), pulls models, and runs docker-compose on Debian/Ubuntu-like hosts.
# Usage: INSTALL_ALL_MODELS=true ./Install_Linux.sh
#        OLLAMA_MODELS="mistral" ./Install_Linux.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DEFAULT_MODELS="mistral"
PIPELINE_MODELS="deepseek-coder-v2:latest gemma3:12b llama3.1:70b gemma3:27b qwen2.5-coder:7b codellama:7b gemma3:4b magicoder:latest"
if [[ "${INSTALL_ALL_MODELS:-}" == "true" ]]; then
  OLLAMA_MODELS="${PIPELINE_MODELS} ${DEFAULT_MODELS}"
else
  OLLAMA_MODELS="${OLLAMA_MODELS:-$DEFAULT_MODELS}"
fi

log() { echo "[$(date +%H:%M:%S)] $*"; }

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    log "Missing required command: $1"
    exit 1
  fi
}

ensure_base_tools() {
  require_command sudo
  if ! command -v curl >/dev/null 2>&1; then
    log "Installing curl..."
    sudo apt-get update -y
    sudo apt-get install -y curl
  fi
}

ensure_docker() {
  if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    log "Docker already installed."
    return
  fi

  log "Installing Docker using the official convenience script..."
  curl -fsSL https://get.docker.com | sudo sh
  sudo systemctl enable --now docker
}

ensure_compose_plugin() {
  if docker compose version >/dev/null 2>&1; then
    return
  fi
  if command -v docker-compose >/dev/null 2>&1; then
    return
  fi
  log "Installing docker-compose-plugin..."
  sudo apt-get update -y
  sudo apt-get install -y docker-compose-plugin
}

ensure_java() {
  if ! command -v java >/dev/null 2>&1; then
    log "Installing OpenJDK runtime..."
    sudo apt-get update -y
    sudo apt-get install -y default-jre
  else
    log "Java already installed."
  fi
}

ensure_ollama() {
  if command -v ollama >/dev/null 2>&1; then
    log "Ollama already installed."
    return
  fi
  log "Installing Ollama (bind to 0.0.0.0:11434 for Docker access)..."
  curl -fsSL https://ollama.com/install.sh | OLLAMA_HOST=0.0.0.0:11434 OLLAMA_ORIGINS="*" sudo sh
}

start_ollama_daemon() {
  if curl -sf http://localhost:11434/api/version >/dev/null 2>&1; then
    log "Ollama daemon already running."
    return
  fi
  log "Starting Ollama daemon..."
  sudo systemctl enable --now ollama || {
    log "Falling back to manual start of ollama serve..."
    OLLAMA_HOST="0.0.0.0:11434" OLLAMA_ORIGINS="*" nohup ollama serve >/tmp/ollama-serve.log 2>&1 &
  }

  for _ in {1..20}; do
    if curl -sf http://localhost:11434/api/version >/dev/null 2>&1; then
      log "Ollama daemon is up."
      return
    fi
    sleep 2
  done

  log "Ollama daemon did not become ready; check /tmp/ollama-serve.log or systemctl status ollama."
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
    log "Docker Compose not found even after install attempt."
    exit 1
  fi
}

run_compose() {
  local compose_cmd
  compose_cmd="$(detect_compose)"
  log "Running '${compose_cmd} up --build -d' from ${ROOT_DIR}"
  (cd "${ROOT_DIR}" && sudo ${compose_cmd} up --build -d)
}

main() {
  log "Starting Linux setup..."
  ensure_base_tools
  ensure_docker
  ensure_compose_plugin
  ensure_java
  ensure_ollama
  start_ollama_daemon
  pull_models
  run_compose
  log "Setup complete."
}

main "$@"

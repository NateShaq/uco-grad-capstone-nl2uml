#requires -version 5.1
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Installs and configures Docker Desktop, Ollama, Java, pulls models, and runs docker compose on Windows.
# Usage examples:
#   powershell -ExecutionPolicy Bypass -File .\Install_Windows.ps1
#   $env:INSTALL_ALL_MODELS='true'; powershell -ExecutionPolicy Bypass -File .\Install_Windows.ps1
#   $env:OLLAMA_MODELS='mistral llama3'; powershell -ExecutionPolicy Bypass -File .\Install_Windows.ps1

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition

$defaultModels = 'mistral'
$pipelineModels = 'deepseek-coder-v2:latest gemma3:12b llama3.1:70b gemma3:27b qwen2.5-coder:7b codellama:7b gemma3:4b magicoder:latest'
if ($env:INSTALL_ALL_MODELS -eq 'true') {
  $ollamaModels = "$pipelineModels $defaultModels"
} elseif ($env:OLLAMA_MODELS) {
  $ollamaModels = $env:OLLAMA_MODELS
} else {
  $ollamaModels = $defaultModels
}

function Write-Log {
  param([string]$Message)
  Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] $Message"
}

function Assert-Admin {
  $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
  $principal = [Security.Principal.WindowsPrincipal] $identity
  if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Run this script in an elevated PowerShell (Run as Administrator).'
  }
}

function Ensure-Winget {
  if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    throw 'winget is required. Install App Installer from the Microsoft Store, then re-run.'
  }
}

function Ensure-DockerDesktop {
  if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Log 'Installing Docker Desktop via winget...'
    winget install -e --id Docker.DockerDesktop --silent
  } else {
    Write-Log 'Docker already installed.'
  }

  Write-Log 'Ensuring Docker Desktop is running...'
  Start-Process -FilePath "C:\Program Files\Docker\Docker\Docker Desktop.exe" -ArgumentList '--unattended' -WindowStyle Minimized -ErrorAction SilentlyContinue | Out-Null

  for ($i = 0; $i -lt 30; $i++) {
    if ((docker info >$null 2>&1)) {
      Write-Log 'Docker daemon is up.'
      return
    }
    Start-Sleep -Seconds 2
  }
  throw 'Docker daemon did not become ready. Open Docker Desktop manually, then re-run.'
}

function Ensure-Java {
  if (-not (Get-Command java -ErrorAction SilentlyContinue)) {
    Write-Log 'Installing OpenJDK via winget...'
    winget install -e --id EclipseAdoptium.TemurinJRE-17 --silent
  } else {
    Write-Log 'Java already installed.'
  }
}

function Ensure-Ollama {
  if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Log 'Installing Ollama via winget...'
    winget install -e --id Ollama.Ollama --silent
  } else {
    Write-Log 'Ollama already installed.'
  }
}

function Start-Ollama {
  if ((Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:11434/api/version' -Method Get -TimeoutSec 3 -ErrorAction SilentlyContinue)) {
    Write-Log 'Ollama daemon already running.'
    return
  }

  Write-Log 'Starting Ollama bound to 0.0.0.0:11434...'
  $env:OLLAMA_HOST = '0.0.0.0:11434'
  $env:OLLAMA_ORIGINS = '*'
  Start-Process -FilePath (Get-Command ollama).Source -ArgumentList 'serve' -WindowStyle Hidden -PassThru | Out-Null

  for ($i = 0; $i -lt 20; $i++) {
    try {
      Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:11434/api/version' -Method Get -TimeoutSec 3 | Out-Null
      Write-Log 'Ollama daemon is up.'
      return
    } catch {
      Start-Sleep -Seconds 2
    }
  }
  throw 'Ollama daemon did not become ready.'
}

function Pull-Models {
  $models = $ollamaModels -split '\s+'
  foreach ($model in $models) {
    if (-not $model) { continue }
    Write-Log "Pulling model: $model"
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = (Get-Command ollama).Source
    $psi.ArgumentList.Add('pull')
    $psi.ArgumentList.Add($model)
    $psi.RedirectStandardOutput = $false
    $psi.RedirectStandardError = $false
    $psi.UseShellExecute = $true
    $proc = [Diagnostics.Process]::Start($psi)
    $proc.WaitForExit()
    if ($proc.ExitCode -ne 0) {
      throw "Failed to pull model $model"
    }
  }
}

function Get-ComposeCommand {
  if ((docker compose version) -ne $null) {
    return 'docker compose'
  }
  if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
    return 'docker-compose'
  }
  throw 'Docker Compose not found.'
}

function Run-Compose {
  $composeCmd = Get-ComposeCommand
  Write-Log "Running '$composeCmd up --build -d' from $ScriptRoot"
  Push-Location $ScriptRoot
  try {
    & $composeCmd up --build -d
  } finally {
    Pop-Location
  }
}

function Main {
  Write-Log 'Starting Windows setup...'
  Assert-Admin
  Ensure-Winget
  Ensure-DockerDesktop
  Ensure-Java
  Ensure-Ollama
  Start-Ollama
  Pull-Models
  Run-Compose
  Write-Log 'Setup complete.'
}

Main

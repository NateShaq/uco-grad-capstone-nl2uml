# app/bootstrap.py
import os
import sys

sys.modules["infrastructure.bootstrap"] = sys.modules[__name__]

# --- Repos used in fallback paths ---
from .infrastructure.repositories.sqlite_model_repository import SqliteDiagramRepository
from .infrastructure.repositories.model_store_repository import (
    ModelStoreDiagramRepository,  # diagram repo adapter over ModelStore (SQLite/JSON)
    ModelStoreAdapter,            # pk/sk model store adapter for InfrastructureService
)
from .infrastructure.repositories.sqlite_user_repository import SqliteUserRepository
from .infrastructure.repositories.sqlite_command_history_repository import SqliteCommandHistoryRepository

# --- Agent factory (function-style preferred) ---
try:
    from .infrastructure.internal.agent_factory import create_agent
except Exception:
    from .infrastructure.internal.agent_factory import AgentFactory as _AgentFactory
    def create_agent(agent_type: str, **kwargs):
        return _AgentFactory.create_agent(agent_type, **kwargs)

from .application.application_service import ApplicationService
from .infrastructure.infrastructure_service import InfrastructureService

# --- Domain services ---
from .domain.domain_access import DomainAccess
from .domain.internal.prompt_template_service import PromptTemplateService

# --- In-memory repos (users/commands always available; models only in USE_INMEM_REPO path) ---
from .domain.internal.user_repository_memory import InMemoryUserRepository as LocalUserRepository
from .domain.internal.command_history_repository_memory import InMemoryCommandHistoryRepository as LocalCommandRepo

# --- Optional Dynamo repos ---
try:
    import boto3
    from .infrastructure.internal.user_repository_dynamodb import UserRepositoryDynamoDB
    from .infrastructure.internal.model_repository_dynamodb import ModelRepositoryDynamoDB
    from .infrastructure.internal.command_repository_dynamodb import CommandRepositoryDynamoDB
except Exception:
    boto3 = None
    UserRepositoryDynamoDB = None
    ModelRepositoryDynamoDB = None
    CommandRepositoryDynamoDB = None

# --- WebSocket / presentation ---
from .infrastructure.internal.websockets import WebSocketPushService
from .presentation.internal.websocket_dispatcher import WebSocketDispatcher

def _use_dynamodb() -> bool:
    env_true = os.environ.get("USE_DYNAMODB", "").lower() in ("1", "true", "yes", "on")
    required = ("AWS_REGION", "USERS_TABLE", "MODELS_TABLE", "COMMANDS_TABLE")
    have_all = all(os.environ.get(k) for k in required)
    return env_true or have_all
def _use_inmem() -> bool:
    return os.environ.get("USE_INMEM_REPO", "").lower() in ("1", "true", "yes", "on")
def _sqlite_exists() -> bool:
    """Detect local SQLite presence (explicit path or default location)."""
    p = os.getenv("SQLITE_DB_PATH", "/var/lib/nl2uml/db/nl2uml.sqlite")
    return os.path.exists(p) or os.path.exists(os.path.dirname(p))
def _build_repositories():
    """
    Return (user_repo, model_repo, command_repo) with precedence:
      1) USE_INMEM_REPO=1  → force all in-memory repos (no persistence)
      2) Dynamo configured → Dynamo repos
      3) SQLite present    → SqliteDiagramRepository (Dynamo-compatible API)
      4) Default           → ModelStoreDiagramRepository (SQLite/JSON via ModelStore)
    """
    # 1) force pure in-memory
    if _use_inmem():
        from .domain.internal.model_repository_memory import InMemoryModelRepository as LocalModelRepository
        return LocalUserRepository(), LocalModelRepository(), LocalCommandRepo()

    # 2) Dynamo
    if _use_dynamodb() and boto3 and UserRepositoryDynamoDB and ModelRepositoryDynamoDB and CommandRepositoryDynamoDB:
        ddb = boto3.resource("dynamodb", region_name=os.environ.get("AWS_REGION"))
        return (
            UserRepositoryDynamoDB(ddb.Table(os.environ["USERS_TABLE"])),
            ModelRepositoryDynamoDB(ddb.Table(os.environ["MODELS_TABLE"])),
            CommandRepositoryDynamoDB(ddb.Table(os.environ["COMMANDS_TABLE"]))
        )

    # 3) SQLite present → use Dynamo-compatible SQLite repo
    if _sqlite_exists():
        return SqliteUserRepository(), SqliteDiagramRepository(), SqliteCommandHistoryRepository()

    # 4) LAST resort (file JSON model store adapter)
    return LocalUserRepository(), ModelStoreDiagramRepository(), SqliteCommandHistoryRepository()
def _selected_agent() -> str:
    for name in ("AI_AGENT_TYPE", "AGENT", "AGENT_TYPE", "AI_AGENT"):
        v = os.getenv(name)
        if v:
            return v.strip()
    return "ollama"
def _build_agent_client():
    selected = _selected_agent()
    try:
        # You can pass env-driven kwargs if desired:
        # return create_agent(selected, host=os.getenv("OLLAMA_HOST"), model=os.getenv("OLLAMA_MODEL"))
        return create_agent(selected)
    except Exception as e:
        print(f"[bootstrap] Failed to create agent '{selected}': {e}. Falling back to 'gronk'.")
        return create_agent("gronk")
def _build_websockets():
    dispatcher = WebSocketDispatcher()
    connections_table = os.environ.get("CONNECTIONS_TABLE")
    ws_api_domain = os.environ.get("WS_API_DOMAIN")
    ws_api_stage = os.environ.get("WS_API_STAGE")

    try:
        push_service = WebSocketPushService(
            connections_table_name=connections_table,
            ws_api_domain=ws_api_domain,
            ws_api_stage=ws_api_stage,
        )
    except Exception as e:
        print(f"[ws] Falling back to NO-OP push service due to init error: {e}")

        class _Noop:
            def push(self, *a, **k):
                return False

            def push_message_to_user(self, *a, **k):
                return False
        push_service = _Noop()

    return dispatcher, push_service
def build_application_service_injection() -> ApplicationService:
    """Composition root for the NL2UML app."""
    # --- Agent & infra: pass pk/sk-capable store adapter into InfrastructureService ---
    agent_client = _build_agent_client()
    infra = InfrastructureService(agent_client, store=ModelStoreAdapter())

    # --- Domain ---
    user_repo, model_repo, command_repo = _build_repositories()
    prompt_templates = PromptTemplateService()
    domain = DomainAccess(
        user_repo=user_repo,
        model_repository=model_repo,
        prompt_template_service=prompt_templates,
        command_repo=command_repo,
    )

    # --- Presentation / WebSockets ---
    _dispatcher, websocket_push = _build_websockets()

    # --- Final application facade ---
    app_service = ApplicationService(
        infra=infra,
        domain=domain,
        websocket_service=websocket_push,
    )

    # Smoke-test user DB write on startup to surface SQLite issues early.
    try:
        test_email = os.getenv("DEV_USER_EMAIL", "startup.smoke@example.com")
        db_path = getattr(user_repo, "db_path", "<unknown>")
        user_repo.create_user(test_email)
        proj_list = []
        if hasattr(user_repo, "list_projects"):
            proj_list = user_repo.list_projects(test_email) or []
        print(f"[bootstrap] SQLite user repo startup smoke test ok for {test_email} (db={db_path}, projects={len(proj_list)})")
    except Exception as exc:
        print(f"[bootstrap] SQLite user repo startup smoke test FAILED: {exc}")

    return app_service

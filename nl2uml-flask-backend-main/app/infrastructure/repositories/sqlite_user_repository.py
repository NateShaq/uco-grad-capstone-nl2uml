from __future__ import annotations
import json
import os
import sqlite3
import time
from datetime import datetime
from typing import Any, Dict, List, Optional


class SqliteUserRepository:
    """
    Simple SQLite-backed user store to persist projects/diagrams between restarts.
    Mirrors the in-memory repo surface so existing callers keep working.
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        # Default to a user-specific DB file to avoid contention with other SQLite users.
        default_path = "/var/lib/nl2uml/db/users.sqlite"
        self.db_path = db_path or os.getenv("SQLITE_USERS_DB_PATH") or default_path
        print(f"[SqliteUserRepository] using db_path={self.db_path}")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._conn() as cx:
            self._ensure_schema(cx)

    def _conn(self):
        # Longer timeout + WAL mode reduces "database is locked" errors under concurrent access.
        cx = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30.0)
        cx.execute("PRAGMA journal_mode=WAL;")
        cx.execute("PRAGMA synchronous=NORMAL;")
        cx.execute("PRAGMA busy_timeout=30000;")
        cx.row_factory = sqlite3.Row
        return cx

    def _ensure_schema(self, cx: sqlite3.Connection) -> None:
        cx.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
              email TEXT PRIMARY KEY,
              projects TEXT NOT NULL,
              diagrams TEXT NOT NULL,
              createdAt TEXT NOT NULL
            )
            """
        )
        cx.commit()

    @staticmethod
    def _key(email: str) -> str:
        return (email or "").lower()

    @staticmethod
    def _row_to_user(row: sqlite3.Row) -> Dict[str, Any]:
        projects = []
        diagrams = []
        try:
            projects = json.loads(row["projects"] or "[]")
        except Exception:
            projects = []
        try:
            diagrams = json.loads(row["diagrams"] or "[]")
        except Exception:
            diagrams = []
        return {
            "email": row["email"],
            "projects": projects,
            "diagrams": diagrams,
            "createdAt": row["createdAt"],
        }

    def _get_or_create(self, email: str) -> Dict[str, Any]:
        user = self.get_user(email)
        if user:
            return user
        return self.create_user(email)

    def _with_retry(self, func, retries: int = 5, delay: float = 0.1):
        import time as _time
        start = _time.perf_counter()
        # Log start/end to track if we ever hang in here
        print("[SqliteUserRepository] _with_retry start")
        last_exc = None
        for attempt in range(retries):
            try:
                if attempt > 0:
                    print(f"[SqliteUserRepository] retry attempt {attempt}")
                result = func()
                elapsed = _time.perf_counter() - start
                print(f"[SqliteUserRepository] _with_retry success after {elapsed:.4f}s")
                return result
            except sqlite3.OperationalError as exc:
                last_exc = exc
                msg = str(exc).lower()
                if "locked" in msg or "busy" in msg:
                    sleep_for = delay * (attempt + 1)
                    print(f"[SqliteUserRepository] database locked, sleeping {sleep_for:.3f}s (attempt {attempt + 1}/{retries})")
                    _time.sleep(sleep_for)
                    continue
                raise
        # Final attempt (let exception bubble so we know)
        print(f"[SqliteUserRepository] _with_retry final attempt after {retries} retries")
        return func()

    def create_user(self, email: str, projects: Optional[List[Dict[str, Any]]] = None, diagrams: Optional[List[Dict[str, Any]]] = None, **fields) -> Dict[str, Any]:
        projects = projects or []
        diagrams = diagrams or []
        now = datetime.utcnow().isoformat()
        record = {
            "email": self._key(email),
            "projects": json.dumps(projects),
            "diagrams": json.dumps(diagrams),
            "createdAt": now,
        }

        def _insert():
            with self._conn() as cx:
                cx.execute(
                    """INSERT INTO users (email, projects, diagrams, createdAt)
                       VALUES (:email, :projects, :diagrams, :createdAt)
                       ON CONFLICT(email) DO NOTHING""",
                    record,
                )
        self._with_retry(_insert)
        return {"email": record["email"], "projects": projects, "diagrams": diagrams, "createdAt": now, **fields}

    def get_user(self, email: Optional[str] = None, **kwargs) -> Optional[Dict[str, Any]]:
        email = self._key(email or kwargs.get("user_id"))
        if not email:
            return None
        with self._conn() as cx:
            row = cx.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
            return self._row_to_user(row) if row else None

    # ---- Projects ----
    def list_projects(self, email: str) -> List[Dict[str, Any]]:
        return list(self._get_or_create(email)["projects"])

    def add_project(self, email: str, project: Dict[str, Any]) -> None:
        user = self._get_or_create(email)
        user["projects"].append(project)
        self.update_projects(email, user["projects"])

    def delete_project(self, email: str, project_id: str) -> None:
        user = self._get_or_create(email)
        projects = [p for p in user["projects"] if p.get("projectId") != project_id]
        self.update_projects(email, projects)

    def update_projects(self, email: str, projects: List[Dict[str, Any]]) -> None:
        email_key = self._key(email)

        def _update():
            now = datetime.utcnow().isoformat()
            t_conn = time.perf_counter()
            with self._conn() as cx:
                print(f"[SqliteUserRepository] update_projects open conn in {time.perf_counter() - t_conn:.4f}s")
                t_exec = time.perf_counter()
                cx.execute(
                    """
                    INSERT INTO users (email, projects, diagrams, createdAt)
                    VALUES (?, ?, '[]', ?)
                    ON CONFLICT(email) DO UPDATE SET projects=excluded.projects
                    """,
                    (email_key, json.dumps(projects), now),
                )
                print(f"[SqliteUserRepository] upsert projects execute in {time.perf_counter() - t_exec:.4f}s")
                cx.commit()
                print("[SqliteUserRepository] update_projects commit done")

        self._with_retry(_update)

    # ---- Diagrams (optional parity with in-memory repo) ----
    def list_diagrams(self, email: str) -> List[Dict[str, Any]]:
        return list(self._get_or_create(email)["diagrams"])

    def add_diagram(self, email: str, diagram: Dict[str, Any]) -> None:
        user = self._get_or_create(email)
        user["diagrams"].append(diagram)
        self.update_diagrams(email, user["diagrams"])

    def delete_diagram(self, email: str, diagram_id: str) -> None:
        user = self._get_or_create(email)
        diagrams = [d for d in user["diagrams"] if d.get("diagramId") != diagram_id]
        self.update_diagrams(email, diagrams)

    def update_diagrams(self, email: str, diagrams: List[Dict[str, Any]]) -> None:
        email_key = self._key(email)

        def _update():
            with self._conn() as cx:
                cx.execute(
                    "UPDATE users SET diagrams=? WHERE email=?",
                    (json.dumps(diagrams), email_key),
                )
                if cx.total_changes == 0:
                    self.create_user(email, diagrams=diagrams)

        self._with_retry(_update)

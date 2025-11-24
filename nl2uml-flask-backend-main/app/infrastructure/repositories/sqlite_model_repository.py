# app/infrastructure/repositories/sqlite_model_repository.py
from __future__ import annotations
import os, sqlite3
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

_SCHEMA = """
CREATE TABLE IF NOT EXISTS diagrams (
  PK          TEXT NOT NULL,
  SK          TEXT NOT NULL,
  projectId   TEXT NOT NULL,
  userEmail   TEXT NOT NULL,
  name        TEXT NOT NULL,
  diagramType TEXT NOT NULL,
  plantuml    TEXT,
  createdAt   TEXT NOT NULL,
  PRIMARY KEY (PK, SK)
);
CREATE INDEX IF NOT EXISTS idx_diagrams_projectId ON diagrams(projectId);
CREATE INDEX IF NOT EXISTS idx_diagrams_userEmail ON diagrams(userEmail);
"""

_EXPECTED_COLUMNS = ("PK", "SK", "projectId", "userEmail", "name", "diagramType", "plantuml", "createdAt")
_LEGACY_COLUMNS = ("id", "project_id", "title")

class SqliteDiagramRepository:
    """
    Dynamo-compatible interface:
      - get_by_id(diagram_id)
      - get_by_project(project_id)
      - get_diagram(user_email, project_id, diagram_id)   [parity with original]
      - save(diagram_id, diagram_item)
      - delete(diagram_id)
    """
    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = db_path or os.getenv("SQLITE_DB_PATH", "/var/lib/nl2uml/db/nl2uml.sqlite")
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
        cols = self._table_columns(cx, "diagrams")
        if not cols:
            cx.executescript(_SCHEMA)
            return

        if not self._has_expected_schema(cols):
            self._migrate_schema(cx, cols)

        # Ensure indexes exist even if schema already matches.
        cx.executescript(_SCHEMA)

    @staticmethod
    def _table_columns(cx: sqlite3.Connection, table: str) -> List[str]:
        cur = cx.execute(f"PRAGMA table_info({table})")
        return [row["name"] for row in cur.fetchall()]

    @staticmethod
    def _has_expected_schema(columns: List[str]) -> bool:
        return all(col in columns for col in _EXPECTED_COLUMNS)

    def _migrate_schema(self, cx: sqlite3.Connection, columns: List[str]) -> None:
        """Rename the legacy table, create the Dynamo-compatible schema, and port what we can."""
        cx.execute("ALTER TABLE diagrams RENAME TO diagrams_legacy")
        cx.executescript(_SCHEMA)

        legacy_cols = set(columns)
        if all(col in legacy_cols for col in _LEGACY_COLUMNS):
            fallback_email = os.getenv("DEV_USER_EMAIL", "demo.user@example.com")
            rows = cx.execute("SELECT id, project_id, title FROM diagrams_legacy").fetchall()
            now = datetime.utcnow().isoformat()
            for row in rows:
                cx.execute(
                    """INSERT INTO diagrams (PK, SK, projectId, userEmail, name, diagramType, plantuml, createdAt)
                       VALUES (?, 'DIAGRAM', ?, ?, ?, '', '', ?)""",
                    (
                        row["id"],
                        row["project_id"] or "",
                        fallback_email,
                        row["title"] or row["id"],
                        now,
                    ),
                )

        cx.execute("DROP TABLE IF EXISTS diagrams_legacy")

    # ----- Dynamo parity -----

    @staticmethod
    def _row_to_diagram(row: sqlite3.Row) -> Dict[str, Any]:
        """Normalize SQLite row to the Dynamo-style payload the app expects."""
        as_dict = dict(row)
        as_dict.setdefault("diagramId", as_dict.get("PK"))
        return {
            "diagramId": as_dict.get("diagramId"),
            "projectId": as_dict.get("projectId"),
            "userEmail": as_dict.get("userEmail"),
            "name": as_dict.get("name"),
            "diagramType": as_dict.get("diagramType"),
            "plantuml": as_dict.get("plantuml"),
            "createdAt": as_dict.get("createdAt"),
        }

    def get_by_id(self, diagram_id: str) -> Optional[Dict[str, Any]]:
        with self._conn() as cx:
            row = cx.execute(
                "SELECT * FROM diagrams WHERE PK=? AND SK='DIAGRAM'", (diagram_id,)
            ).fetchone()
            return self._row_to_diagram(row) if row else None

    def get_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        with self._conn() as cx:
            cur = cx.execute(
                "SELECT * FROM diagrams WHERE projectId=? ORDER BY createdAt DESC", (project_id,)
            )
            return [self._row_to_diagram(r) for r in cur.fetchall()]

    def get_diagram(self, user_email: str, project_id: str, diagram_id: str) -> Optional[Dict[str, Any]]:
        with self._conn() as cx:
            row = cx.execute(
                """SELECT * FROM diagrams
                   WHERE PK=? AND SK='DIAGRAM' AND projectId=? AND userEmail=?""",
                (diagram_id, project_id, user_email)
            ).fetchone()
            return self._row_to_diagram(row) if row else None

    def save(self, diagram_id: str, diagram_item: Dict[str, Any]) -> None:
        with self._conn() as cx:
            cx.execute(
                """INSERT INTO diagrams
                   (PK, SK, projectId, userEmail, name, diagramType, plantuml, createdAt)
                   VALUES (:PK, 'DIAGRAM', :projectId, :userEmail, :name, :diagramType, :plantuml, :createdAt)
                   ON CONFLICT(PK, SK) DO UPDATE SET
                       projectId=excluded.projectId,
                       userEmail=excluded.userEmail,
                       name=excluded.name,
                       diagramType=excluded.diagramType,
                       plantuml=excluded.plantuml,
                       createdAt=excluded.createdAt
                """,
                {
                    "PK": diagram_id,
                    "projectId": diagram_item.get("projectId"),
                    "userEmail": diagram_item.get("userEmail"),
                    "name": diagram_item.get("name"),
                    "diagramType": diagram_item.get("diagramType"),
                    "plantuml": diagram_item.get("plantuml"),
                    "createdAt": diagram_item.get("createdAt"),
                }
            )

    def delete(self, diagram_id: str) -> None:
        with self._conn() as cx:
            cx.execute("DELETE FROM diagrams WHERE PK=? AND SK='DIAGRAM'", (diagram_id,))

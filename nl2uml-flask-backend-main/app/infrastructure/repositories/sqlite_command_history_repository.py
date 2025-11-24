from __future__ import annotations
import os, sqlite3
from typing import Dict, Optional

from app.domain.internal.command_history_repository import CommandHistoryRepository

_SCHEMA = """
CREATE TABLE IF NOT EXISTS command_history (
  diagramId     TEXT NOT NULL,
  commandId     TEXT NOT NULL,
  timestamp     INTEGER NOT NULL,
  userEmail     TEXT NOT NULL,
  projectId     TEXT NOT NULL,
  commandType   TEXT NOT NULL,
  plantumlBefore TEXT,
  plantumlAfter  TEXT,
  isCurrent     INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (diagramId, commandId)
);
CREATE INDEX IF NOT EXISTS idx_command_history_diagram_ts ON command_history(diagramId, timestamp);
"""

class SqliteCommandHistoryRepository(CommandHistoryRepository):
    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = db_path or os.getenv("SQLITE_DB_PATH", "/var/lib/nl2uml/db/nl2uml.sqlite")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._conn() as cx:
            cx.executescript(_SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        cx = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30.0)
        # Keep SQLite settings consistent across all repos to minimize lock contention.
        cx.execute("PRAGMA journal_mode=WAL;")
        cx.execute("PRAGMA synchronous=NORMAL;")
        cx.execute("PRAGMA busy_timeout=30000;")
        cx.row_factory = sqlite3.Row
        return cx

    def record_refine(
        self,
        *,
        diagram_id: str,
        user_email: str,
        project_id: str,
        command_id: str,
        timestamp: int,
        plantuml_before: str,
        plantuml_after: str,
    ) -> None:
        with self._conn() as cx:
            current = self._current(cx, diagram_id)
            if current:
                cx.execute(
                    "DELETE FROM command_history WHERE diagramId=? AND timestamp>? ",
                    (diagram_id, current["timestamp"]),
                )
                cx.execute(
                    "UPDATE command_history SET isCurrent=0 WHERE diagramId=?",
                    (diagram_id,),
                )
            else:
                # seed baseline snapshot so undo has somewhere to go back to
                cx.execute(
                    """INSERT OR IGNORE INTO command_history
                       (diagramId, commandId, timestamp, userEmail, projectId, commandType,
                        plantumlBefore, plantumlAfter, isCurrent)
                       VALUES (?, ?, ?, ?, ?, 'BASE', ?, ?, 0)""",
                    (
                        diagram_id,
                        f"base-{diagram_id}",
                        max(timestamp - 1, 0),
                        user_email,
                        project_id,
                        plantuml_before or "",
                        plantuml_before or "",
                    ),
                )

            cx.execute(
                """INSERT INTO command_history
                   (diagramId, commandId, timestamp, userEmail, projectId, commandType,
                    plantumlBefore, plantumlAfter, isCurrent)
                   VALUES (?, ?, ?, ?, ?, 'RefineDiagram', ?, ?, 1)""",
                (
                    diagram_id,
                    command_id,
                    timestamp,
                    user_email,
                    project_id,
                    plantuml_before or "",
                    plantuml_after or "",
                ),
            )

    def undo(self, diagram_id: str, user_email: str, project_id: str) -> Optional[Dict[str, str]]:
        with self._conn() as cx:
            cmds = self._all(cx, diagram_id)
            if not cmds:
                return None
            current_idx = self._current_index(cmds)
            if current_idx is None or current_idx == 0:
                return None
            current = cmds[current_idx]
            prev_cmd = cmds[current_idx - 1]
            cx.execute(
                "UPDATE command_history SET isCurrent=0 WHERE diagramId=? AND commandId=?",
                (diagram_id, current["commandId"]),
            )
            cx.execute(
                "UPDATE command_history SET isCurrent=1 WHERE diagramId=? AND commandId=?",
                (diagram_id, prev_cmd["commandId"]),
            )
            return {
                "diagramId": diagram_id,
                "plantuml": prev_cmd["plantumlAfter"] or "",
                "message": "Undo successful",
            }

    def redo(self, diagram_id: str, user_email: str, project_id: str) -> Optional[Dict[str, str]]:
        with self._conn() as cx:
            cmds = self._all(cx, diagram_id)
            if not cmds:
                return None
            current_idx = self._current_index(cmds)
            if current_idx is None or current_idx >= len(cmds) - 1:
                return None
            current = cmds[current_idx]
            next_cmd = cmds[current_idx + 1]
            cx.execute(
                "UPDATE command_history SET isCurrent=0 WHERE diagramId=? AND commandId=?",
                (diagram_id, current["commandId"]),
            )
            cx.execute(
                "UPDATE command_history SET isCurrent=1 WHERE diagramId=? AND commandId=?",
                (diagram_id, next_cmd["commandId"]),
            )
            return {
                "diagramId": diagram_id,
                "plantuml": next_cmd["plantumlAfter"] or "",
                "message": "Redo successful",
            }

    def _current(self, cx: sqlite3.Connection, diagram_id: str):
        return cx.execute(
            "SELECT * FROM command_history WHERE diagramId=? AND isCurrent=1 LIMIT 1",
            (diagram_id,),
        ).fetchone()

    def _all(self, cx: sqlite3.Connection, diagram_id: str):
        return cx.execute(
            "SELECT * FROM command_history WHERE diagramId=? ORDER BY timestamp ASC",
            (diagram_id,),
        ).fetchall()

    @staticmethod
    def _current_index(cmds):
        for idx, cmd in enumerate(cmds):
            if cmd["isCurrent"]:
                return idx
        return None

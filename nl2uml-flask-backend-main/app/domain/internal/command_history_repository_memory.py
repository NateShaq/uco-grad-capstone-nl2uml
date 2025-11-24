from __future__ import annotations
from typing import Any, Dict, List, Optional
from .command_history_repository import CommandHistoryRepository

class InMemoryCommandHistoryRepository(CommandHistoryRepository):
    def __init__(self):
        # diagramId -> list[command]
        self._history: Dict[str, List[Dict[str, Any]]] = {}

    def _commands(self, diagram_id: str) -> List[Dict[str, Any]]:
        cmds = self._history.setdefault(diagram_id, [])
        cmds.sort(key=lambda c: c["timestamp"])
        return cmds

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
        cmds = self._commands(diagram_id)
        # Remove redo stack (anything after current)
        current_idx = next((i for i, c in enumerate(cmds) if c.get("isCurrent")), None)
        if current_idx is not None:
            cmds[:] = cmds[: current_idx + 1]
            cmds[current_idx]["isCurrent"] = False
        elif not cmds:
            # seed baseline snapshot for undo
            cmds.append(
                {
                    "commandId": f"base-{diagram_id}",
                    "timestamp": timestamp - 1,
                    "plantumlAfter": plantuml_before,
                    "userEmail": user_email,
                    "projectId": project_id,
                    "isCurrent": False,
                }
            )

        cmds.append(
            {
                "commandId": command_id,
                "timestamp": timestamp,
                "plantumlBefore": plantuml_before,
                "plantumlAfter": plantuml_after,
                "userEmail": user_email,
                "projectId": project_id,
                "isCurrent": True,
            }
        )

    def undo(self, diagram_id: str, user_email: str, project_id: str) -> Optional[Dict[str, str]]:
        cmds = self._commands(diagram_id)
        if not cmds:
            return None
        current_idx = next((i for i, c in enumerate(cmds) if c.get("isCurrent")), None)
        if current_idx is None or current_idx == 0:
            return None
        cmds[current_idx]["isCurrent"] = False
        cmds[current_idx - 1]["isCurrent"] = True
        prev_cmd = cmds[current_idx - 1]
        return {
            "diagramId": diagram_id,
            "plantuml": prev_cmd.get("plantumlAfter", ""),
            "message": "Undo successful",
        }

    def redo(self, diagram_id: str, user_email: str, project_id: str) -> Optional[Dict[str, str]]:
        cmds = self._commands(diagram_id)
        if not cmds:
            return None
        current_idx = next((i for i, c in enumerate(cmds) if c.get("isCurrent")), None)
        if current_idx is None or current_idx >= len(cmds) - 1:
            return None
        cmds[current_idx]["isCurrent"] = False
        cmds[current_idx + 1]["isCurrent"] = True
        next_cmd = cmds[current_idx + 1]
        return {
            "diagramId": diagram_id,
            "plantuml": next_cmd.get("plantumlAfter", ""),
            "message": "Redo successful",
        }

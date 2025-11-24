# app/domain/internal/model_repository_memory.py
from __future__ import annotations
from typing import Dict, List, Optional

class InMemoryModelRepository:
    """
    Minimal in-memory diagram repo that matches the methods your services call.
    This mirrors the DynamoDB repo surface (get_by_id, get_by_project, get_diagram, save, delete).
    """

    def __init__(self):
        # store by diagramId
        self._by_id: Dict[str, dict] = {}
        # index diagrams by projectId -> [diagramId, ...]
        self._by_project: Dict[str, List[str]] = {}

    # ---- Reads ----
    def get_by_id(self, diagram_id: str) -> Optional[dict]:
        return self._by_id.get(diagram_id)

    def get_by_project(self, project_id: str) -> List[dict]:
        ids = self._by_project.get(project_id, [])
        return [self._by_id[i] for i in ids if i in self._by_id]

    def get_diagram(self, user_email: str, project_id: str, diagram_id: str) -> Optional[dict]:
        d = self._by_id.get(diagram_id)
        if not d:
            return None
        # optional guards to mimic multi-tenant filtering
        if project_id and d.get("projectId") != project_id:
            return None
        if user_email and d.get("userEmail") not in (None, user_email):
            # if you want strict ownership
            pass
        return d

    # ---- Writes ----
    def save(self, diagram_id: str, diagram_item: dict) -> dict:
        # normalize item shape to match your Dynamo writer
        item = {
            "diagramId": diagram_item.get("diagramId", diagram_id),
            "projectId": diagram_item.get("projectId"),
            "userEmail": diagram_item.get("userEmail"),
            "name": diagram_item.get("name"),
            "diagramType": diagram_item.get("diagramType"),
            "plantuml": diagram_item.get("plantuml"),
            "createdAt": diagram_item.get("createdAt"),
            # include any other fields you rely on (updatedAt, etc.)
        }
        self._by_id[diagram_id] = item

        pid = item.get("projectId")
        if pid:
            self._by_project.setdefault(pid, [])
            if diagram_id not in self._by_project[pid]:
                self._by_project[pid].append(diagram_id)

        return item

    def delete(self, diagram_id: str) -> bool:
        item = self._by_id.pop(diagram_id, None)
        if not item:
            return False
        pid = item.get("projectId")
        if pid and pid in self._by_project:
            self._by_project[pid] = [i for i in self._by_project[pid] if i != diagram_id]
            if not self._by_project[pid]:
                self._by_project.pop(pid, None)
        return True
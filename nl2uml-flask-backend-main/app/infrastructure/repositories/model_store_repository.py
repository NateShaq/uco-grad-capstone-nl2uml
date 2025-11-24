from __future__ import annotations
from typing import Any, Dict, List, Optional
from app.infrastructure.internal.model_store import ModelStore, BaseModelStore

class ModelStoreDiagramRepository:
    """
    Adapts BaseModelStore (get/put/delete/list) to the diagram repo interface
    expected by DiagramManager/ApplicationService.
    Persists diagram records in a DynamoDB-like flat structure compatible with SQLite.
    """
    def __init__(self, store: Optional[BaseModelStore] = None):
        self.store: BaseModelStore = store or ModelStore()

    def save(self, diagram_id: str, diagram_item: Dict[str, Any]) -> None:
        """Persist a diagram entity into the underlying store."""
        print(f"[ModelStoreDiagramRepository] Saving diagram {diagram_id} with item: {diagram_item}")
        import datetime
        item = dict(diagram_item)
        item.setdefault("id", diagram_id)
        item.setdefault("type", "diagram")
        item.setdefault("createdAt", datetime.datetime.utcnow().isoformat())
        item.setdefault("sk", "DIAGRAM")  # emulate Dynamo sort key for consistency
        item.setdefault("pk", diagram_id) # useful for debugging or portability

        print(f"[ModelStoreDiagramRepository] Saving diagram {diagram_id}")
        self.store.put(item)

    def get_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        """Return all diagrams for a given project."""
        return [it for it in self.store.list() if it.get("projectId") == project_id]

    def get_by_id(self, diagram_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single diagram by its id."""
        return self.store.get(diagram_id)

    def delete(self, diagram_id: str) -> None:
        """Remove a diagram from the store."""
        print(f"[ModelStoreDiagramRepository] Deleting diagram {diagram_id}")
        self.store.delete(diagram_id)

class ModelStoreAdapter:
    def __init__(self, store: Optional[BaseModelStore] = None) -> None:
        # Use whichever backend the ModelStore factory returns (SQLite, JSON, etc.)
        self._store = store or ModelStore()

    def save(self, pk: str, sk: str, value: str) -> None:
        """Save a model blob under composite key pk#sk."""
        print("ModelStoreAdapter saving:", pk, sk)
        item = {
            "id": f"{pk}#{sk}",
            "type": "model",   # Tag for filtering / clarity
            "pk": pk,
            "sk": sk,
            "value": value,
        }
        self._store.put(item)

    def retrieve(self, pk: str, sk: str) -> str:
        """Retrieve model blob for pk#sk."""
        item = self._store.get(f"{pk}#{sk}") or {}
        return item.get("value", "")

    def cleanup_old_models(self) -> None:
        """Placeholder for TTL cleanup logic."""
        return

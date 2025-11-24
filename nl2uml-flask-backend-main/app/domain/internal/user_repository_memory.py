# from __future__ import annotations
# from typing import Any, Dict
# from .user_repository import UserRepository

# class InMemoryUserRepository(UserRepository):
#     def __init__(self):
#         self._users: Dict[str, Dict[str, Any]] = {}

#     # Adjust the signatures to exactly match the ABC!
#     def create_user(self, user_id: str, **fields):
#         self._users[user_id] = {"id": user_id, **fields}
#         return self._users[user_id]

#     def get_user(self, user_id: str):
#         return self._users.get(user_id)

# app/infrastructure/repositories/inmemory_user_repository.py
from __future__ import annotations
from typing import Any, Dict, List, Optional

class InMemoryUserRepository:
    """
    In-memory user store keyed by email.
    Returns plain dicts so callers can safely do `user.get(...)`.
    """

    def __init__(self):
        # normalized (lowercased) email -> user dict
        self._users: Dict[str, Dict[str, Any]] = {}

    # ---------- helpers ----------
    def _key(self, email: str) -> str:
        return (email or "").lower()

    def _get_or_create(self, email: str) -> Dict[str, Any]:
        k = self._key(email)
        if k not in self._users:
            self._users[k] = {
                "email": email,
                "projects": [],   # list of project dicts
                "diagrams": [],   # optional: list of diagram dicts if your code uses it
            }
        return self._users[k]

    # ---------- API used by services ----------
    def create_user(self, email: str, **fields) -> Dict[str, Any]:
        u = self._get_or_create(email)
        # persist any extra fields (e.g., name, claims)
        u.update({k: v for k, v in fields.items() if v is not None})
        return u

    # Accept both `email=` and legacy positional/kw so call sites won't break
    def get_user(self, email: Optional[str] = None, **kwargs) -> Optional[Dict[str, Any]]:
        email = email or kwargs.get("user_id")
        if not email:
            return None
        return self._users.get(self._key(email))

    # ---- Projects ----
    def list_projects(self, email: str) -> List[Dict[str, Any]]:
        return list(self._get_or_create(email)["projects"])

    def add_project(self, email: str, project: Dict[str, Any]) -> None:
        u = self._get_or_create(email)
        u["projects"].append(project)

    def delete_project(self, email: str, project_id: str) -> None:
        u = self._get_or_create(email)
        u["projects"] = [p for p in u["projects"] if p.get("projectId") != project_id]

    def update_projects(self, email: str, projects: List[Dict[str, Any]]) -> None:
        # Replace the full project list (some services use this pattern)
        u = self._get_or_create(email)
        u["projects"] = list(projects)

    # ---- (Optional) Diagrams, if your service touches these on the user ----
    def list_diagrams(self, email: str) -> List[Dict[str, Any]]:
        return list(self._get_or_create(email)["diagrams"])

    def add_diagram(self, email: str, diagram: Dict[str, Any]) -> None:
        u = self._get_or_create(email)
        u["diagrams"].append(diagram)

    def delete_diagram(self, email: str, diagram_id: str) -> None:
        u = self._get_or_create(email)
        u["diagrams"] = [d for d in u["diagrams"] if d.get("diagramId") != diagram_id]

    def update_diagrams(self, email: str, diagrams: List[Dict[str, Any]]) -> None:
        u = self._get_or_create(email)
        u["diagrams"] = list(diagrams)
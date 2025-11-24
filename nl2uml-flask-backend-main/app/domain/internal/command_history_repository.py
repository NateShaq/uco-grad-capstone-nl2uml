from abc import ABC, abstractmethod
from typing import Dict, Optional

class CommandHistoryRepository(ABC):
    @abstractmethod
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
        """Persist a refine command snapshot for undo/redo."""

    @abstractmethod
    def undo(self, diagram_id: str, user_email: str, project_id: str) -> Optional[Dict[str, str]]:
        """Move the cursor back one command and return the resulting plantuml snapshot."""

    @abstractmethod
    def redo(self, diagram_id: str, user_email: str, project_id: str) -> Optional[Dict[str, str]]:
        """Move the cursor forward one command and return the resulting plantuml snapshot."""

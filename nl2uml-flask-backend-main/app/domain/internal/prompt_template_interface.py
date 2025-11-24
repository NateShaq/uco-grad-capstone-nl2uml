from __future__ import annotations
from abc import ABC, abstractmethod


class PromptTemplate(ABC):
    @abstractmethod
    def build_prompt(self, user_prompt: str, related_plantuml: str = None) -> str:
        """Build a final prompt ready for AI generation."""
        pass

    @abstractmethod
    def requires_related_plantuml(self) -> bool:
        """Whether this template needs to fetch related PlantUML data."""
        return False  # Most templates don't need it unless overridden

    def build_pipeline_prompts(self, user_prompt: str, related_plantuml: str = None) -> dict | None:
        """
        Optional: Provide specialized prompts for the multi-model pipeline.
        Return a dict like:
        {
          "diagram_type": "class|sequence|use_case|activity|component|state",
          "ideation_prompt": "...",        # optional; if None, ideation is skipped
          "uml_prompt": "...",             # required; final UML generation prompt
          "uml_prompt_uses_analyst_notes": bool  # if True, pipeline formats with analyst notes
        }
        """
        return None

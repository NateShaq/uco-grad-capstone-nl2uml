from .prompt_template_interface import PromptTemplate

class StatePromptTemplate(PromptTemplate):
    def build_prompt(self, user_prompt: str, related_plantuml: str = None) -> str:
        return (
            "DiagramType: state\n"
            "You are a UML modeling expert specializing in State Diagrams.\n"
            "Generate a PlantUML state machine for the entity described below using the correct state-diagram syntax:\n\n"
            f"{user_prompt}\n\n"
            "Requirements:\n"
            "- Use `state` blocks (e.g., `state Idle { ... }`) and the `[ * ]` notation for initial/final states.\n"
            "- Define transitions with `StateA --> StateB : event / action` lines.\n"
            "- Use `state if`, `state fork`, etc., only when the behavior calls for them; avoid class or component keywords.\n"
            "- Output only PlantUML between @startuml and @enduml."
        )
        
    def requires_related_plantuml(self) -> bool:
        return False

    def build_pipeline_prompts(self, user_prompt: str, related_plantuml: str = None) -> dict:
        uml_prompt = (
            "You are a UML modeling expert specializing in State Diagrams.\n"
            "Output ONLY valid PlantUML between @startuml and @enduml with no markdown fences or commentary.\n"
            "- Use `state` blocks and [*] for initial/final states; include transitions with `A --> B : event / action`.\n"
            "- Avoid class/component keywords; keep syntax tight and valid.\n\n"
            f"Generate the state diagram for:\n{user_prompt}\n"
        )
        return {
            "diagram_type": "state",
            "ideation_prompt": None,
            "uml_prompt": uml_prompt,
            "uml_prompt_uses_analyst_notes": False,
        }

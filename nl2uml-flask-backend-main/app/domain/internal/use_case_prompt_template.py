from .prompt_template_interface import PromptTemplate

class UseCasePromptTemplate(PromptTemplate):
    def build_prompt(self, user_prompt: str, related_plantuml: str = None) -> str:
        return (
            "DiagramType: use_case\n"
            "You are a PlantUML use-case expert.\n"
            "Produce a clean, minimal diagram that still follows PlantUML syntax perfectly.\n\n"
            "Rules:\n"
            "- Output only PlantUML between @startuml and @enduml (no code fences or macros).\n"
            "- Declare actors with `actor` or `:Actor:`; declare use cases with `(Name)` or `usecase UC as \"Name\"`.\n"
            "- Place use cases inside a `package`/`rectangle` if a system boundary is needed. Packages will use { } brackets to wrap usecases. Package names must contain no spaces, use underscores if needed in place of spaces.\n"
            "- Connect actors to use cases with `-->`; use `<|--` for actor generalization and `.>` for include/extend arrows (with labels like `<<include>>`).\n"
            "- Optional: tidy layout with `left to right direction`, `skinparam actorStyle`/`packageStyle`, or simple notes using `note left/right of Element ... end note`.\n"
            "- No commentary outside the UML block and no unsupported directives.\n\n"
            "Generate the requested diagram:\n"
            f"{user_prompt}\n"
        )
        
    def requires_related_plantuml(self) -> bool:
        return False

    def build_pipeline_prompts(self, user_prompt: str, related_plantuml: str = None) -> dict:
        uml_prompt = (
            "You are a PlantUML use-case expert.\n"
            "Output ONLY valid PlantUML between @startuml and @enduml with no markdown fences or explanations.\n"
            "- Declare actors with `actor` or `:Actor:`; use cases with `(Name)` or `usecase UC as \"Name\"`.\n"
            "- Connect actors to use cases with `-->`; use `<|--` for actor generalization and `.>` for include/extend arrows with labels.\n"
            "- Optional: use packages/rectangles for system boundaries; package names should avoid spaces.\n\n"
            f"Generate the requested use-case diagram from:\n{user_prompt}\n"
        )
        return {
            "diagram_type": "use_case",
            "ideation_prompt": None,
            "uml_prompt": uml_prompt,
            "uml_prompt_uses_analyst_notes": False,
        }


# Actors
# Use Cases
# System Boundary (Package/Rectangle)
# Relationships
# Association
    # Include
    # Extend
    # Generalization
    # Notes / Annotations
# Stereotypes

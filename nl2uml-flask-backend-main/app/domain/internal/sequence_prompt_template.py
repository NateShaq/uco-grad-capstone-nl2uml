from .prompt_template_interface import PromptTemplate

class SequencePromptTemplate(PromptTemplate):

    def requires_related_plantuml(self) -> bool:
        return True

    def build_prompt(self, user_prompt: str, related_plantuml: str = None) -> str:
        extra_context = ""
        if related_plantuml:
            extra_context = (
                "\nUse this related Class Diagram as context for participants and messages:\n"
                f"```plantuml\n{related_plantuml}\n```"
            )

        return (
            "DiagramType: sequence\n"
            "You are an expert in PlantUML Sequence Diagrams.\n\n"
            "Generate a valid PlantUML sequence diagram using ONLY this format:\n"
            "@startuml\n"
            "...sequence interactions...\n"
            "@enduml\n\n"
            "Include only the essential participants (use simple aliases like A1, S1, etc.) and the key messages between them.\n"
            "Do not declare participants that never send or receive a message in the diagram.\n"
            "Do not add explanations or text outside the code block.\n"
            "Do not add any text lines before @startuml or after @enduml.\n"
            "Do not use spaces in participant aliases.\n"
            "Define participants explicitly at the top of the diagram, e.g. `participant StudentAccount as A1`.\n\n"
            "The system description is:\n"
            f"\"{user_prompt}\"\n"
            f"{extra_context}\n"
        )

    def build_pipeline_prompts(self, user_prompt: str, related_plantuml: str = None) -> dict:
        extra_context = ""
        if related_plantuml:
            extra_context = (
                "\nUse this related Class Diagram as context for participants and messages:\n"
                f"{related_plantuml}\n"
            )
        uml_prompt = (
            "You are an expert in PlantUML Sequence Diagrams.\n"
            "Output ONLY valid PlantUML wrapped by @startuml and @enduml with no markdown fences or commentary.\n"
            "- Define participants explicitly (no spaces in aliases).\n"
            "- Include only participants that send or receive messages.\n"
            "- Keep focus on key interactions and lifelines.\n\n"
            f"System description:\n{user_prompt}\n"
            f"{extra_context}\n"
        )
        return {
            "diagram_type": "sequence",
            "ideation_prompt": None,
            "uml_prompt": uml_prompt,
            "uml_prompt_uses_analyst_notes": False,
        }


# Participants / Lifelines
# Messages (sync, async, return, self, etc.)
# Activation / Deactivation
# Groups / Control Structures
# Notes / Annotations
# Creation / Destruction
# Separators (==, ..., |||)
# References (ref over)
# Stereotypes
# Boxes / Containers
from .use_case_prompt_template import UseCasePromptTemplate
from .activity_prompt_template import ActivityPromptTemplate
from .component_prompt_template import ComponentPromptTemplate
from .class_prompt_template import ClassPromptTemplate
from .sequence_prompt_template import SequencePromptTemplate
from .state_prompt_template import StatePromptTemplate

class PromptTemplateFactory:
    @staticmethod
    def get_template(diagram_type: str):
        print(f"Diagram type requested: {diagram_type}")
        if diagram_type == "use_case":
            return UseCasePromptTemplate()
        elif diagram_type == "activity":
            return ActivityPromptTemplate()
        elif diagram_type == "component":
            return ComponentPromptTemplate()
        elif diagram_type == "class":
            return ClassPromptTemplate()
        elif diagram_type == "sequence":
            return SequencePromptTemplate()
        elif diagram_type == "state":
            return StatePromptTemplate()
        else:
            raise ValueError(f"Unknown diagram type: {diagram_type}")
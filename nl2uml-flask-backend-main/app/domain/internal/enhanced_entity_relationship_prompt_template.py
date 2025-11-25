from .prompt_template_interface import PromptTemplate


class EnhancedEntityRelationshipPromptTemplate(PromptTemplate):
    def build_prompt(self, user_prompt: str, related_plantuml: str = None) -> str:
        return (
            "DiagramType: eerd\n"
            "You are a PlantUML expert who emulates Enhanced Entity Relationship Diagrams (EERDs) using PlantUML entity/class syntax.\n"
            "Because PlantUML has no native EERD, express entities with `entity` blocks and annotated associations.\n\n"
            "Rules:\n"
            "- Output ONLY PlantUML between @startuml and @enduml (no markdown fences or explanations).\n"
            "- Model each entity with `entity Name { ... }` and list attributes inside.\n"
            "- Mark primary keys with `{PK}` and foreign keys with `{FK}` beside the attribute name; place keys before non-key attributes and separate sections with `--` when mixing.\n"
            "- Draw relationships with straight associations (`--`); include cardinality labels on both ends using quoted multiplicities (e.g., `Order \"0..*\" -- \"1\" Customer`).\n"
            "- Use inheritance (`<|--`) only when the prompt clearly describes specialization/generalization.\n"
            "- Keep styling light; ensure every referenced entity exists and braces are balanced.\n\n"
            "Create the enhanced entity relationship diagram for:\n"
            f"{user_prompt}\n"
        )

    def requires_related_plantuml(self) -> bool:
        return False

    def build_pipeline_prompts(self, user_prompt: str, related_plantuml: str = None) -> dict:
        ideation_prompt = (
            "You are a data modeling expert.\n"
            "Given a natural-language description, return ONLY JSON describing the entities for an Enhanced Entity Relationship Diagram (EERD).\n"
            "Do NOT add commentary.\n\n"
            "JSON format:\n"
            "{\n"
            '  \"entities\": [\n'
            "    {\n"
            '      \"name\": \"string\",\n'
            '      \"description\": \"string\",\n'
            '      \"attributes\": [\n'
            '        { \"name\": \"string\", \"type\": \"string\", \"role\": \"pk|fk|regular\", \"references\": \"TargetEntity.attribute|\\\"\\\"\" }\n'
            "      ],\n"
            '      \"subtypes\": [\"ChildEntity\", \"...\"]\n'
            "    }\n"
            "  ],\n"
            '  \"relationships\": [\n'
            "    {\n"
            '      \"from\": \"string\",\n'
            '      \"to\": \"string\",\n'
            '      \"type\": \"identifying|non_identifying|inheritance\",\n'
            '      \"cardinalityFrom\": \"0..1|1|0..*|1..*\",\n'
            '      \"cardinalityTo\": \"0..1|1|0..*|1..*\",\n'
            '      \"description\": \"string\"\n'
            "    }\n"
            "  ]\n"
            "}\n\n"
            "Now analyze the following description and output ONLY valid JSON in that structure:\n\n"
            f"{user_prompt}"
        )

        uml_prompt = (
            "You are an expert PlantUML author generating Enhanced Entity Relationship Diagrams using PlantUML entity syntax.\n"
            "Output ONLY:\n"
            "@startuml\n"
            "...diagram...\n"
            "@enduml\n\n"
            "Mapping rules:\n"
            "- Each item in entities → `entity Name {{ ... }}`.\n"
            "- List PK attributes first, marked `{{PK}}`; FK attributes marked `{{FK}}` and optionally note the reference in the attribute name.\n"
            "- Separate key attributes from others with `--` when both exist.\n"
            "- For relationships type:\n"
            "  - identifying → `A *-- B`\n"
            "  - non_identifying → `A -- B`\n"
            "  - inheritance → `A <|-- B`\n"
            "- Always include cardinalities as quoted labels on both ends (e.g., `A \"1\" -- \"0..*\" B`).\n"
            "- Ensure every referenced entity exists and syntax is valid PlantUML.\n\n"
            "Here is the JSON model to convert:\n"
            "{analyst_notes}\n\n"
            "Return ONLY PlantUML."
        )

        return {
            "diagram_type": "class",  # leverage class diagram pipeline for ideation + validation
            "ideation_prompt": ideation_prompt,
            "uml_prompt": uml_prompt,
            "uml_prompt_uses_analyst_notes": True,
        }

from .prompt_template_interface import PromptTemplate

class ClassPromptTemplate(PromptTemplate):
    def build_prompt(self, user_prompt: str, related_plantuml: str = None) -> str:
        return (
            "DiagramType: class\n"
            "You are a PlantUML class-diagram expert.\n"
            "Generate the simplest valid diagram that satisfies the request.\n\n"
            "Rules:\n"
            "- Output only PlantUML between @startuml and @enduml (no extra commentary).\n"
            "- Declare every structured element with an explicit keyword (`class Foo { ... }`, `interface Bar`, `enum Baz`); never open a block like `Foo {` without the keyword.\n"
            "- Whenever the user describes relationships, include them explicitly using the right connector: `--` or `-->` for associations/dependencies, `<|--` for inheritance/generalization, `..|>` for interface implementation, `o--` for aggregation, and `*--` for composition.\n"
            "- Keep layout clean; optional helpers like `package`, `note`, or `skinparam` are fine but stay lightweight.\n"
            "- Ensure every arrow target exists and that braces/blocks are balanced.\n\n"
            "Build the requested class diagram:\n"
            f"{user_prompt}\n"
        )
    def requires_related_plantuml(self) -> bool:
        return False
    def build_pipeline_prompts(self, user_prompt: str, related_plantuml: str = None) -> dict:
        ideation_prompt = (
            "You are a senior software architect.\n"
            "Given a short natural-language description of a software system, you MUST respond in a strict JSON structure that describes the domain model and key use cases.\n"
            "DO NOT write explanations, only valid JSON.\n\n"
            "JSON format:\n"
            "{\n"
            '  \"boundedContexts\": [\n'
            "    {\n"
            '      \"name\": \"string\",\n'
            '      \"description\": \"string\",\n'
            '      \"entities\": [\n'
            "        {\n"
            '          \"name\": \"string\",\n'
            '          \"description\": \"string\",\n'
            '          \"attributes\": [\n'
            '            { \"name\": \"string\", \"type\": \"string\", \"description\": \"string\" }\n'
            "          ],\n"
            '          \"operations\": [\n'
            '            { \"name\": \"string\", \"description\": \"string\" }\n'
            "          ]\n"
            "        }\n"
            "      ],\n"
            '      \"valueObjects\": [\n'
            '        { \"name\": \"string\", \"description\": \"string\" }\n'
            "      ],\n"
            '      \"services\": [\n'
            "        {\n"
            '          \"name\": \"string\",\n'
            '          \"description\": \"string\",\n'
            '          \"operations\": [\n'
            '            { \"name\": \"string\", \"description\": \"string\" }\n'
            "          ]\n"
            "        }\n"
            "      ],\n"
            '      \"relationships\": [\n'
            "        {\n"
            '          \"from\": \"string\",\n'
            '          \"to\": \"string\",\n'
            '          \"type\": \"association|aggregation|composition|inheritance\",\n'
            '          \"description\": \"string\"\n'
            "        }\n"
            "      ],\n"
            '      \"useCases\": [\n'
            "        {\n"
            '          \"name\": \"string\",\n'
            '          \"primaryActor\": \"string\",\n'
            '          \"summary\": \"string\"\n'
            "        }\n"
            "      ]\n"
            "    }\n"
            "  ]\n"
            "}\n\n"
            "Now analyze the following system description and return ONLY JSON in that format, no extra text.\n\n"
            f"{user_prompt}"
        )

        uml_prompt = (
            "You are an expert PlantUML Class Diagram generator.\n"
            "Your task is to take a JSON description of a domain model and output ONLY valid PlantUML code for a class diagram.\n"
            "RULES:\n"
            "1. Output MUST be:\n"
            "   @startuml\n"
            "   ...classes and relations...\n"
            "   @enduml\n\n"
            "2. Do NOT include markdown fences or explanations or actors.\n"
            "3. Every class must come from an \"entities\" or \"services\" entry.\n"
            "4. Map JSON to UML like this:\n"
            "   - entities → class\n"
            "   - services → class with «service» stereotype\n"
            "   - attributes → fields\n"
            "   - operations → methods\n"
            "   - relationships.type:\n"
            "       - association  → A --> B\n"
            "       - aggregation  → A o-- B\n"
            "       - composition  → A *-- B\n"
            "       - inheritance  → A <|-- B\n\n"
            "5. Use simple types (string, int, decimal, date, boolean) as-is.\n"
            "6. Validate the UML for syntactic correctness before returning. Ensure all classes start with 'class' keyword\n\n"
            "Here is the JSON domain model:\n"
            "{analyst_notes}\n\n"
            "The model outputs:"
        )

        return {
            "diagram_type": "class",
            "ideation_prompt": ideation_prompt,
            "uml_prompt": uml_prompt,
            "uml_prompt_uses_analyst_notes": True,
        }


# Classes
    # Attributes (Fields)
    # Methods (Operations)
# Interfaces
# Abstract Classes
# Enumerations (Enums)
# Stereotypes / Annotations
# Relationships
    # Inheritance
    # Implementation
    # Composition
    # Aggregation
    # Association
    # Dependency
# Association Classes
# Packages / Namespaces
# Notes


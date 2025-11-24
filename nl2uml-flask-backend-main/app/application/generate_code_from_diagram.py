from typing import Dict
import json

class GenerateCodeFromDiagram:
    def __init__(self, app_service: "ApplicationService"):
        self.app = app_service

    def execute(self, user_email: str, body: Dict) -> Dict:
        diagram_id = body.get("diagramId")
        project_id = body.get("projectId")
        target_language = body.get("targetLanguage", "").lower()
        agent_type = body.get("agentType", "openai")

        if not all([diagram_id, project_id, target_language]):
            raise ValueError("diagramId, projectId, and targetLanguage are required.")

        diagram_item = self.app.get_diagram(user_email, project_id, diagram_id)
        plantuml_text = diagram_item.get("plantuml", "")

        prompt = (
            f"Convert the following UML description into {target_language.upper()} source code. "
            f"Only output valid {target_language.upper()} code, starting immediately with class definitions or top-level structures. "
            f"Do not include explanations, comments, or any extra text.\n\n"
            f"```plantuml\n{plantuml_text}\n```"
        )

        code_output = self.app.generate_code_from_uml(prompt, agent_type=agent_type)
        return {
            "diagramId": diagram_id,
            "language": target_language,
            "code": code_output
        }
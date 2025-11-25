from typing import Dict

class GenerateDiagram:
    """
    Generates and stores a UML diagram using an AI agent based on user input.
    """
    def __init__(self, app_service: "ApplicationService"):
        self.app = app_service

    def execute(self, user_email: str, body: Dict) -> Dict:
        name = body.get("name")
        project_id = body.get("projectId")
        diagram_type = body.get("diagramType", "")
        prompt = body.get("prompt", "")
        agent_type = body.get("AI_Agent", "").lower().strip() or "openai"
        pipeline_models = body.get("ollamaModels") or body.get("ollama_models")

        print(f"[nlp_agent] GenerateDiagram")

        if not all([name, project_id, diagram_type, prompt]):
            raise ValueError("Missing required parameters in request body")

        print("Diagram type ABC:", diagram_type)

        try:
            polished_prompt, pipeline_prompts = self.app.generate_prompt_with_template(
                user_email=user_email,
                project_id=project_id,
                name=name,
                diagram_type=diagram_type,
                prompt=prompt,
                agent_type=agent_type 
            )

            print(f"[nlp_agent] GenerateDiagram12 with polished prompt:", polished_prompt)

            response_json = self.app.generate_and_save_diagram(
                user_email=user_email,
                project_id=project_id,
                name=name,
                diagram_type=diagram_type,
                prompt=polished_prompt,
                pipeline_prompts=pipeline_prompts,
                agent_type=agent_type,
                pipeline_models=pipeline_models,
            )
            return response_json
        except Exception as exc:
            import traceback
            print("[nlp_agent] GenerateDiagram encountered error:", repr(exc))
            print(traceback.format_exc())
            raise

import json
import uuid
from datetime import datetime

class DiagramManager:
    def __init__(self, diagram_repo):
        self.diagram_repo = diagram_repo

    def create_diagram(self, event, user_email, project_id):
        data = json.loads(event['body'])
        diagram_id = str(uuid.uuid4())
        item = {
            "diagramId": diagram_id,
            "projectId": project_id,
            "userEmail": user_email,
            "name": data.get('name'),
            "diagramType": data.get('diagramType', ''),
            "plantuml": data.get('plantuml', ''),
            "createdAt": datetime.utcnow().isoformat()
        }
        self.diagram_repo.save(diagram_id, item)
        return {"statusCode": 201, "body": json.dumps(item)}

    def list_diagrams(self, user_email, project_id):
        diagrams = self.diagram_repo.get_by_project(project_id)
        return {"statusCode": 200, "body": json.dumps({"diagrams": diagrams})}

    def get_diagram(self, user_email, diagram_id):
        diagram = self.diagram_repo.get_by_id(diagram_id)
        if not diagram:
            return {"statusCode": 404, "body": json.dumps({"error": "Diagram not found"})}
        return {"statusCode": 200, "body": json.dumps(diagram)}

    def delete_diagram(self, user_email, diagram_id):
        self.diagram_repo.delete(diagram_id)
        return {"statusCode": 204, "body": json.dumps({})}
import json
import uuid
import time

class ProjectManager:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    def create_project(self, event, user_email):
        t0 = time.perf_counter()
        data = json.loads(event['body'])
        print(f"[ProjectManager] Parsing body done in {time.perf_counter() - t0:.4f}s")
        name = data['name']
        description = data.get('description', '')
        project_id = str(uuid.uuid4())

        t_user = time.perf_counter()
        user = self.user_repo.get_user(user_email) or {"projects": []}
        print(f"[ProjectManager] user_repo.get_user in {time.perf_counter() - t_user:.4f}s")
        projects = user.get('projects', [])

        project = {"projectId": project_id, "name": name, "description": description}
        t_append = time.perf_counter()
        projects.append(project)
        print(f"[ProjectManager] append project in {time.perf_counter() - t_append:.6f}s")
        t_update = time.perf_counter()
        self.user_repo.update_projects(email=user_email, projects=projects)
        print(f"[ProjectManager] user_repo.update_projects in {time.perf_counter() - t_update:.4f}s")

        total = time.perf_counter() - t0
        print(f"[ProjectManager] create_project total time {total:.4f}s")
        return {"statusCode": 201, "body": json.dumps(project)}

    def list_projects(self, user_email):
        user = self.user_repo.get_user(user_email) or {}
        return {"statusCode": 200, "body": json.dumps({"projects": user.get('projects', [])})}

    def get_project(self, user_email, project_id):
        user = self.user_repo.get_user(user_email)
        if not user:
            return {"statusCode": 404, "body": json.dumps({"error": "User not found"})}
        for proj in user.get('projects', []):
            if proj['projectId'] == project_id:
                return {"statusCode": 200, "body": json.dumps(proj)}
        return {"statusCode": 404, "body": json.dumps({"error": "Project not found"})}

    def delete_project(self, user_email, project_id):
        user = self.user_repo.get_user(user_email)
        if not user or 'projects' not in user:
            return {"statusCode": 404, "body": json.dumps({"error": "Project or user not found"})}
        projects = [p for p in user['projects'] if p['projectId'] != project_id]
        if len(projects) == len(user['projects']):
            return {"statusCode": 404, "body": json.dumps({"error": "Project not found"})}
        self.user_repo.update_projects(email=user_email, projects=projects)
        return {"statusCode": 204, "body": json.dumps({})}

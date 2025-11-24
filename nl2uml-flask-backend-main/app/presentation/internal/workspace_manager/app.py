import json
import traceback
import time
from app.util.login.auth import resolve_user_email

try:
    from app.bootstrap import build_application_service_injection
except ImportError:
    from ....bootstrap import build_application_service_injection  

service = build_application_service_injection()

ALLOWED_ORIGINS = {"http://localhost:3001", "http://127.0.0.1:3001"}

def _cors_headers(event):
    hdrs = (event.get("headers") or {})
    origin = hdrs.get("Origin") or hdrs.get("origin")
    allow_origin = origin if origin in ALLOWED_ORIGINS else "http://localhost:3001"

    requested = hdrs.get("Access-Control-Request-Headers") or hdrs.get("access-control-request-headers")
    allow_headers = requested if requested else "Content-Type, Authorization, X-Requested-With, Accept, Origin"

    return {
        "Access-Control-Allow-Origin": allow_origin,
        "Vary": "Origin",
        "Access-Control-Allow-Headers": allow_headers,
        "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
        "Access-Control-Max-Age": "600",
    }


def handler(event, context):
    # === Detailed Diagnostics ===
    _start = time.perf_counter()
    print("\n[workspace_manager.handler] ===== Incoming Event =====")
    print(json.dumps({
        "method": event.get("httpMethod"),
        "path": event.get("path"),
        "resource": event.get("resource"),
        "pathParameters": event.get("pathParameters"),
        "queryStringParameters": event.get("queryStringParameters"),
    }, indent=2))
    print("==============================================\n")

    method = event.get("httpMethod")
    if method == "OPTIONS":
        print("[workspace_manager.handler] OPTIONS preflight handled.")
        return {"statusCode": 200, "headers": _cors_headers(event), "body": ""}

    try:
        user_email = resolve_user_email(event)

        path = event.get("resource") or event.get("path")
        params = event.get("pathParameters") or {}
        print(f"[workspace_manager.handler] Dispatching {method} {path} with params: {params}")
        print(f"[workspace_manager.handler] User email resolved to: {user_email}")

        # === Routing Logic ===
        route_start = time.perf_counter()
        if path == "/projects" and method == "POST":
            result = service.create_project(event, user_email)
        elif path == "/projects" and method == "GET":
            result = service.list_projects(user_email)
        elif path == "/projects/{projectId}" and method == "GET":
            result = service.get_project(user_email, params["projectId"])
        elif path == "/projects/{projectId}" and method == "DELETE":
            result = service.delete_project(user_email, params["projectId"])
        elif path == "/projects/{projectId}/diagrams" and method == "POST":
            result = service.create_diagram(event, user_email, params["projectId"])
        elif path == "/projects/{projectId}/diagrams" and method == "GET":
            result = service.list_diagrams(user_email, params["projectId"])
        elif path == "/diagrams/{diagramId}" and method == "GET":
            result = service.get_diagram_by_id(user_email, params["diagramId"])
        elif path == "/diagrams/{diagramId}" and method == "DELETE":
            result = service.delete_diagram(user_email, params["diagramId"])
        else:
            print(f"[workspace_manager.handler] No match for path={path}, method={method}")
            result = {
                "statusCode": 404,
                "body": json.dumps({"error": f"Route not found: {method} {path}"}),
            }
        route_elapsed = time.perf_counter() - route_start
        print(f"[workspace_manager.handler] Route handler time: {route_elapsed:.4f}s")

        # === CORS merge ===
        result["headers"] = {**result.get("headers", {}), **_cors_headers(event)}

        total_elapsed = time.perf_counter() - _start
        print(f"[workspace_manager.handler] → Returning {result.get('statusCode', 0)} after {total_elapsed:.4f}s\n")
        return result

    except KeyError as ke:
        print(f"❌ KeyError in handler: {ke}")
        print(traceback.format_exc())
        return {
            "statusCode": 400,
            "headers": _cors_headers(event),
            "body": json.dumps({"error": f"Missing path parameter: {ke}"}),
        }

    except Exception as e:
        print(f"❌ Unhandled Exception: {e}")
        print(traceback.format_exc())
        return {
            "statusCode": 500,
            "headers": _cors_headers(event),
            "body": json.dumps({"error": f"Internal server error: {str(e)}"}),
        }

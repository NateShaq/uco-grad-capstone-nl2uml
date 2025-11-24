import json
from app.util.login.auth import resolve_user_email


try:
    from app.bootstrap import build_application_service_injection
except ImportError:
    from ....bootstrap import build_application_service_injection  
    

service = build_application_service_injection()

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-User-Email,X-User-Id,X-Session-Id",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE",
}

def _resolve_user_email(event):
    return resolve_user_email(event)

def handler(event, context):
    method = event.get("httpMethod")
    if method == "OPTIONS":
        return {"statusCode": 200, "headers": cors_headers, "body": ""}

    try:
        user_email = _resolve_user_email(event)
        body = json.loads(event.get("body", "{}"))

        # Returns a clean dict like: { "diagramId": ..., "plantuml": ..., "message": "Redo successful" }
        payload = service.handle_redo_request(user_email, body)

        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": json.dumps(payload)
        }

    except Exception as e:
        print("❌ REDO ERROR:", str(e))
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }

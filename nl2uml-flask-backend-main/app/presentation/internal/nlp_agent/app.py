# ==============================
# lambda/generate/index.py
# (Presentation Layer)

import json
import traceback

try:
    from app.bootstrap import build_application_service_injection
except ImportError:
    from ....bootstrap import build_application_service_injection  

from app.util.login.auth import resolve_user_email

service = build_application_service_injection()

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-User-Email,X-User-Id,X-Session-Id",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
}

def handler(event, context):
    method = event.get("httpMethod")
    if method == "OPTIONS":
        return {"statusCode": 200, "headers": cors_headers, "body": ""}

    try:
        user_email = resolve_user_email(event)
        print(f"[nlp_agent] Using user identifier: {user_email}")
        body = json.loads(event.get("body", "{}"))
        print(f"[nlp_agent] HERE 0")

        response = service.handle_generate_request(user_email, body)
        return {"statusCode": 201, "headers": cors_headers, "body": json.dumps(response)}
        
    except ValueError as ve:
        return {"statusCode": 400, "headers": cors_headers, "body": json.dumps({"error": str(ve)})}

    except Exception as e:
        print(f"❌ Error in /generate handler: {str(e)}")
        print(traceback.format_exc())
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }

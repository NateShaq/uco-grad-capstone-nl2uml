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
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,DELETE",
}

def handler(event, context):
    method = event.get('httpMethod')
    if method == "OPTIONS":
        return {"statusCode": 200, "headers": cors_headers, "body": ""}

    try:
        user_email = resolve_user_email(event)
        path = event.get('resource') or event.get('path')

        if path == "/code" and method == "POST":
            body = json.loads(event.get("body", "{}"))
            response_body = service.handle_code_request(user_email, body)
            result = {
                "statusCode": 200,
                "headers": cors_headers,
                "body": json.dumps(response_body)
            }
        else:
            result = {
                "statusCode": 404,
                "headers": cors_headers,
                "body": json.dumps({"error": "Route not found"})
            }

        return result

    except Exception as e:
        print(f"❌ Error in /code handler: {str(e)}")
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }

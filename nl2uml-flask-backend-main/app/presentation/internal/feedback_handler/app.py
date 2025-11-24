import json

from app.util.login.auth import resolve_user_email


try:
    from app.bootstrap import build_application_service_injection
except ImportError:
    from ....bootstrap import build_application_service_injection  

service = build_application_service_injection()

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-User-Email,X-User-Id,X-Session-Id",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
}

def handler(event, context):
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": cors_headers, "body": ""}

    try:
        user_email = resolve_user_email(event)
        body = json.loads(event.get("body", "{}"))
        response = service.handle_refine_request(user_email, body)
        return {"statusCode": 200, "headers": cors_headers, "body": json.dumps(response)}

    except ValueError as ve:
        return {"statusCode": 400, "headers": cors_headers, "body": json.dumps({"error": str(ve)})}

    except Exception as e:
        print(f"❌ Error in /refine handler: {str(e)}")
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }

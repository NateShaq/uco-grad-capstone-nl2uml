import json

try:
    from app.bootstrap import build_application_service_injection
except ImportError:
    from ....bootstrap import build_application_service_injection  


service = build_application_service_injection()

COMMON_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-User-Email',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
}

def handler(event, context):
    try:
        if event.get("httpMethod") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": COMMON_HEADERS,
                "body": json.dumps({"message": "ok"})
            }

        model_id = event.get("queryStringParameters", {}).get("diagramId")
        if not model_id:
            return {
                "statusCode": 400,
                'headers': COMMON_HEADERS,
                "body": json.dumps({"message": "diagramId query parameter is required"})
            }

        explanation = service.explain_model(model_id)
        return {
            "statusCode": 200,
            'headers': COMMON_HEADERS,
            "body": json.dumps({ "explanation": explanation })
        }

    except ValueError as e:
        print(f"❌ Error: {str(e)}")
        status = 400 if "required" in str(e).lower() else 404
        return {
            "statusCode": status,
            'headers': COMMON_HEADERS,
            "body": json.dumps({"message": str(e)})
        }
    except NotImplementedError as e:
        print(f"❌ Error: {str(e)}")
        return {
            "statusCode": 501,
            'headers': COMMON_HEADERS,
            "body": json.dumps({"message": str(e)})
        }
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {
            "statusCode": 500,
            'headers': COMMON_HEADERS,
            "body": f"Internal server error: {str(e)}"
        }

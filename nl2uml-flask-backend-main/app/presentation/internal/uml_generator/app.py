import json

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE",
}

def handler(event, context):
    method = event.get('httpMethod')
    if method == "OPTIONS":
        return {"statusCode": 200, "headers": cors_headers, "body": ""}

    try:
        print(f"🧪 Lambda placeholder invoked: {event.get('resource')} with method {method}")
        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": json.dumps({"message": "Lambda is wired correctly"})
        }

    except Exception as e:
        print(f"❌ Error in stub: {str(e)}")
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }
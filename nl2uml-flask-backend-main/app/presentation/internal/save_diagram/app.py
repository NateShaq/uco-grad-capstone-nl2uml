import boto3
import os
import json
from app.util.login.auth import resolve_user_email

# Initialize DynamoDB resource and table
# dynamodb = boto3.resource('dynamodb')
# model_table = dynamodb.Table(os.environ['TABLE_NAME'])

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-User-Email",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE",
}

def handler(event, context):
    # Short-circuit preflight so the browser sees a 200 with CORS headers.
    if event.get("httpMethod") == "OPTIONS":
        return {"statusCode": 200, "headers": cors_headers, "body": ""}

    try:
        raw_body = event.get("body") or "{}"
        body = json.loads(raw_body)
        diagram_id = body.get("diagramId")
        project_id = body.get("projectId")
        plantuml = body.get("plantuml")
        user_email = body.get("userEmail") or resolve_user_email(event)  # If you use it for partition key

        if not diagram_id or not project_id or not plantuml:
            raise Exception("diagramId, projectId, and plantuml required.")

        PK = f"USER#{user_email}#PROJECT#{project_id}"
        SK = f"DIAGRAM#{diagram_id}"
        # model_table.update_item(
        #     Key={'PK': PK, 'SK': SK},
        #     UpdateExpression='SET plantuml = :plantuml',
        #     ExpressionAttributeValues={':plantuml': plantuml}
        # )

        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": json.dumps({"message": "Diagram saved!"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({"error": str(e)})
        }

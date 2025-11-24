import boto3
from datetime import datetime, timezone, timedelta


try:
    from app.bootstrap import build_application_service_injection
except ImportError:
    from ....bootstrap import build_application_service_injection  
    
service = build_application_service_injection()

def handler(event, context):
    print("WebSocket Push Event:", json.dumps(event))
    domain = os.environ["WS_API_DOMAIN"]
    stage = os.environ["WS_API_STAGE"]
    message = event.get("body", "Diagram updated")

    api = boto3.client("apigatewaymanagementapi",
        endpoint_url=f"https://{domain}/{stage}"
    )

    connection_id = event["requestContext"]["connectionId"]
    
    try:
        api.post_to_connection(
            ConnectionId=connection_id,
            Data=message.encode("utf-8")
        )
    except Exception as e:
        print("Push failed:", e)

    return { 
        "statusCode": 200,
        'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
         }, 
        "body": "Pushed" }

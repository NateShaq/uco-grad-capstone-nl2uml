import boto3
from datetime import datetime, timezone, timedelta

from infrastructure.bootstrap import build_application_service_injection
service = build_application_service_injection()

def handler(event, context):
    s3 = boto3.client('s3')
    bucket = "your-s3-bucket-name"
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    result = s3.list_objects_v2(Bucket=bucket)
    deleted = 0

    for obj in result.get("Contents", []):
        if obj["LastModified"] < cutoff:
            s3.delete_object(Bucket=bucket, Key=obj["Key"])
            deleted += 1

    return {
        "statusCode": 200,
          'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
        },
        "body": f"Deleted {deleted} old files."
    }
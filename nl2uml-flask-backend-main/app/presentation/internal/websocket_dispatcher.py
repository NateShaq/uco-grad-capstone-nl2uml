# app/presentation/internal/websocket_dispatcher.py
try:
    import boto3
except Exception:
    boto3 = None

import os

class WebSocketDispatcher:
    """
    Local/dev: prints or no-ops if AWS config/boto3 isn't present.
    Prod: uses APIGW Management API when boto3 + env vars exist.
    """
    def __init__(self):
        self.domain = os.getenv("WS_API_DOMAIN")
        self.stage = os.getenv("WS_API_STAGE")
        self.enabled = bool(boto3 and self.domain and self.stage)

        if not self.enabled:
            print("[ws] WebSocketDispatcher running in NO-OP mode (boto3 or env missing)")

        if self.enabled:
            self._client = boto3.client(
                "apigatewaymanagementapi",
                endpoint_url=f"https://{self.domain}/{self.stage}",
                region_name=os.getenv("AWS_REGION") or "us-east-1",
            )
        else:
            self._client = None

    def push(self, connection_id_or_model_id: str, payload: dict):
        if not self.enabled:
            # Dev-friendly log
            print(f"[ws noop] push({connection_id_or_model_id}): {payload}")
            return
        try:
            self._client.post_to_connection(
                ConnectionId=connection_id_or_model_id,
                Data=str(payload).encode("utf-8"),
            )
        except Exception as e:
            print(f"[ws] post_to_connection failed: {e}")
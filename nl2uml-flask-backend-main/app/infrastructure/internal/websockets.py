from __future__ import annotations
import os

class WebSocketPushService:
    def __init__(self, connections_table_name=None, ws_api_domain=None, ws_api_stage=None):
        self._table_name = connections_table_name
        self._domain = ws_api_domain
        self._stage = ws_api_stage
        self._enabled = bool(ws_api_domain and ws_api_stage and connections_table_name)
        if self._enabled:
            print("[ws] WebSocketPushService configured (domain/stage/table provided)")
        else:
            print("[ws] WebSocketPushService running in NO-OP mode (missing env or boto3)")
    def push(self, *_, **__) -> bool:
        return False

    def push_message_to_user(self, user_email: str, message: dict) -> bool:
        """
        Local-friendly no-op push helper. When the service is not configured it simply logs.
        If AWS resources are configured later, this method can be expanded to call the API Gateway
        management API or DynamoDB connections table.
        """
        if not self._enabled:
            print(f"[ws] Skipping push to {user_email}: websocket service not configured.")
            return False
        # Placeholder for future real push implementation.
        print(f"[ws] Would push to {user_email}: {message}")
        return True

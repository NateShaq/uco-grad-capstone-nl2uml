import boto3
import os
import json

def get_user_claims(event):
    try:
        claims = event['requestContext']['authorizer']['claims']
        return {
            "sub": claims['sub'],
            "email": claims['email'],
            # Add any other claims you want to always grab
        }
    except (KeyError, TypeError):
        # Optionally, log or raise a custom exception here
        raise Exception("User claims missing from event")

def resolve_user_email(event) -> str:
    """
    Resolve the caller's user identifier with priority:
    1) Custom headers from the frontend: X-User-Email, X-User-Id, X-Session-Id
    2) DEV_BYPASS_AUTH / DEV_USER_EMAIL environment flags
    3) Cognito claims (if present)
    4) Fallback guest email
    """
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    header_email = headers.get("x-user-email") or headers.get("x-user-id") or headers.get("x-session-id")
    if header_email:
        return header_email

    if os.getenv("DEV_BYPASS_AUTH", "0") == "1":
        return os.getenv("DEV_USER_EMAIL", "dev.user@example.com")

    try:
        claims = get_user_claims(event)
        if claims and "email" in claims:
            return claims["email"]
    except Exception:
        pass

    return os.getenv("ANON_USER_EMAIL", "guest@example.com")

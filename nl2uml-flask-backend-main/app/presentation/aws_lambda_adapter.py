import os
import importlib
import json
from flask import request, make_response

ALL_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD")

class AWSLambdaAdapter:
    """
    Adapts Flask HTTP requests to AWS Lambda-style `event` and `context` objects.

    Features:
    - Converts Flask request to Lambda event shape.
    - Dynamically imports and invokes a target Lambda handler.
    - Adds consistent CORS headers for browser clients.
    - Provides a DEV auth shim to inject fake claims when `DEV_BYPASS_AUTH=1`.
    """

    def __init__(self, default_cors_origin="http://localhost:3000"):
        self.default_cors_origin = default_cors_origin

    # ----------------------------
    # Build the Lambda event shape
    # ----------------------------
    def _build_event(self):
        is_json = request.is_json
        raw = request.get_data()            # bytes
        body_str = raw.decode("utf-8", errors="ignore")

        # If Flask parsed JSON, re-dump to a canonical string
        if is_json:
            try:
                body_str = json.dumps(request.get_json(silent=True) or {})
            except Exception:
                # fall back to raw string
                pass

        return {
            "httpMethod": request.method,
            "headers": dict(request.headers),
            "path": request.path,
            "resource": request.path,
            "pathParameters": {},
            "queryStringParameters": dict(request.args),
            "body": body_str,               # string per API Gateway norm
            "isBase64Encoded": False,       # be explicit
        }

    # ----------------------------
    # CORS support
    # ----------------------------
    def _cors_headers(self):
        origin = request.headers.get("Origin") or self.default_cors_origin

        # Always allow our custom headers used by the frontend (X-User-Email) plus any requested ones.
        requested = request.headers.get("Access-Control-Request-Headers")
        allow_headers = "Content-Type, Authorization, X-Requested-With, Accept, Origin, X-User-Email"
        if requested:
            allow_headers = f"{allow_headers}, {requested}"

        return {
            "Access-Control-Allow-Origin": origin,
            "Vary": "Origin",
            "Access-Control-Allow-Headers": allow_headers,
            "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS,HEAD",
            "Access-Control-Max-Age": "600",
        }

    # ----------------------------
    # Flask view factory
    # ----------------------------
    def to_lambda_view(self, target: str, route_path: str):
        """
        Return a Flask view that forwards the request to a Lambda handler.

        Example:
            target="app.presentation.internal.nlp_agent.app:handler"
            route_path="/projects/<projectId>/diagrams"
        """
        def view_func(**path_params):
            print(f"[gateway] Forwarding {request.method} {request.path} -> {target}")
            # 🔧 normalize Flask "<param>" -> API Gateway "{param}"
            normalized_resource = route_path.replace("<", "{").replace(">", "}")

            # Build Lambda-style event using the *template* for "resource"
            event = {
                "httpMethod": request.method,
                "headers": dict(request.headers),
                "path": request.path,                  # e.g. /projects/123/diagrams
                "resource": normalized_resource,       # e.g. /projects/{projectId}/diagrams  ✅
                "pathParameters": path_params or {},   # {"projectId": "..."}
                "queryStringParameters": dict(request.args),
                "body": request.get_data(as_text=True),
                "isBase64Encoded": False,
            }
            # 🔧 DEV auth shim (inject claims for local runs without Cognito/JWT)
            if os.getenv("DEV_BYPASS_AUTH", "0") == "1":
                email = request.headers.get("X-Dev-Email") or os.getenv("DEV_USER_EMAIL", "demo.user@example.com")
                event.setdefault("requestContext", {}).setdefault("authorizer", {})["claims"] = {
                    "email": email,
                    "name": request.headers.get("X-Dev-Name", "Dev User"),
                    "given_name": "Dev",
                    "family_name": "User",
                    "preferred_username": email,
                }
                print(f"[adapter] Injected dev user claims for {email}")

            # Import & invoke the Lambda handler
            module_path, func_name = target.split(":")
            mod = importlib.import_module(module_path)
            handler = getattr(mod, func_name)

            context = {"function_name": func_name, "route": route_path}
            result = handler(event, context)

            # Build Flask response
            status = result.get("statusCode", 200)
            body = result.get("body", "")
            if isinstance(body, str):
                try:
                    body = json.loads(body)
                except json.JSONDecodeError:
                    pass

            resp = make_response(body, status)

            # Merge CORS + any Lambda headers
            headers = {**self._cors_headers(), **result.get("headers", {})}
            for k, v in headers.items():
                resp.headers[k] = v

            return resp

        # Ensure unique endpoint names across different route templates
        view_func.__name__ = (
            f"lambda_view_{target.replace('.', '_').replace(':', '_')}"
            f"_{route_path.replace('/', '_').replace('<', '_').replace('>', '_')}"
        )
        return view_func

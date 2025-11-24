from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from .bootstrap import build_application_service_injection
from .presentation.presentation_gateway import PresentationGateway

import os, sys
_layer = os.path.join(os.path.dirname(__file__), "util", "python")
if _layer not in sys.path:
    sys.path.insert(0, _layer)

ALLOWED_ORIGINS = {"http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"}

def _cors_headers():
    origin = request.headers.get("Origin")
    allow_origin = origin if origin in ALLOWED_ORIGINS else "http://localhost:3001"
    req_headers = request.headers.get("Access-Control-Request-Headers")
    allow_headers = req_headers if req_headers else "Content-Type, Authorization, X-Requested-With, Accept, Origin"
    return {
        "Access-Control-Allow-Origin": allow_origin,
        "Vary": "Origin",
        # If you ever need cookies, switch this to "true" AND don’t use "*"
        # "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Headers": allow_headers,
        "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
        "Access-Control-Max-Age": "600",
    }

def create_app():
    app = Flask(__name__)

    # 1) Catch-all OPTIONS so every preflight gets HTTP 200
    @app.route("/<path:_any>", methods=["OPTIONS"])
    @app.route("/", methods=["OPTIONS"])
    def cors_preflight(_any=None):
        resp = make_response("", 200)
        for k, v in _cors_headers().items():
            resp.headers[k] = v
        return resp

    # 2) Add CORS headers to every normal response
    @app.after_request
    def add_cors(resp):
        for k, v in _cors_headers().items():
            resp.headers.setdefault(k, v)
        return resp

    CORS(
        app,
        resources={r"/*": {"origins": ["http://localhost:3001", "http://127.0.0.1:3001"]}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
        max_age=600,
        supports_credentials=False,
    )

    # Your domain service (if handlers need it via current_app.config)
    app.config["APP_SERVICE"] = build_application_service_injection()

    gateway = PresentationGateway()
    gateway.register(app)
    app.config["GATEWAY"] = gateway

    @app.get("/health")
    def health():
        return jsonify(status="ok", service="nl2uml", ready=True)

    return app

app = create_app()
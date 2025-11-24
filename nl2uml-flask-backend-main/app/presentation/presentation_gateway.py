# presentation_gateway.py
from __future__ import annotations
from typing import List, Tuple
from flask import Flask
from .aws_lambda_adapter import AWSLambdaAdapter, ALL_METHODS

class PresentationGateway:
    def __init__(self, default_cors_origin: str = "http://localhost:3001"):
        self.adapter = AWSLambdaAdapter(default_cors_origin=default_cors_origin)

        self.lambda_routes: List[Tuple[str, str]] = [
            ("/code",                 "app.presentation.internal.code_generator.app:handler"),
            ("/diagrams",             "app.presentation.internal.workspace_manager.app:handler"),
            ("/diagrams/<diagramId>", "app.presentation.internal.workspace_manager.app:handler"),
            ("/explain",              "app.presentation.internal.explain_agent.app:handler"),
            ("/uml/generate",         "app.presentation.internal.nlp_agent.app:handler"),
            ("/projects",             "app.presentation.internal.workspace_manager.app:handler"),
            ("/projects/<projectId>", "app.presentation.internal.workspace_manager.app:handler"),
            ("/projects/<projectId>/diagrams", "app.presentation.internal.workspace_manager.app:handler"),
            ("/redo",                 "app.presentation.internal.redo.app:handler"),
            ("/refine",               "app.presentation.internal.feedback_handler.app:handler"),
            ("/save-diagram",         "app.presentation.internal.save_diagram.app:handler"),
            ("/undo",                 "app.presentation.internal.undo.app:handler"),
            # If you want a param route too, add it explicitly:
            # ("/diagrams/<diagram_id>", "app.presentation.internal.workspace_manager.app:handler"),
        ]

    def register(self, app: Flask):
        for rule, target in self.lambda_routes:
            safe_rule = rule.replace("/", ".").replace("<", "_").replace(">", "_")
            endpoint = f"lambda:{target}:{safe_rule}"
            app.add_url_rule(
                rule,
                endpoint,
                self.adapter.to_lambda_view(target, rule),
                methods=list(ALL_METHODS),
                strict_slashes=False,  # allow trailing slash
            )
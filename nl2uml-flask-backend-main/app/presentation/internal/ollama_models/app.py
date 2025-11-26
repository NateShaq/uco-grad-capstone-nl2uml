import json
import os

from app.infrastructure.internal.ollama_pipeline_client import (
    DEFAULT_IDEATION_MODELS,
    DEFAULT_UML_MODELS,
    DEFAULT_VALIDATION_MODELS,
    MultiOllamaPipelineClient,
    _parse_models,
)

cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-User-Email,X-User-Id,X-Session-Id",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE"
}


def handler(event, context):
    method = event.get("httpMethod")
    if method == "OPTIONS":
        return {"statusCode": 200, "headers": cors_headers, "body": ""}

    if method not in ("GET", None):  # default for flask adapter is None
        return {
            "statusCode": 405,
            "headers": cors_headers,
            "body": json.dumps({"error": "Method not allowed"})
        }

    # Build from environment (or defaults) and filter against the running Ollama host
    client = MultiOllamaPipelineClient()
    ideation_models = client.ideation_models or _parse_models(os.getenv("OLLAMA_IDEATION_MODELS") or DEFAULT_IDEATION_MODELS)
    uml_models = client.uml_models or _parse_models(os.getenv("OLLAMA_UML_MODELS") or DEFAULT_UML_MODELS)
    validation_models = client.validator_models or _parse_models(os.getenv("OLLAMA_VALIDATION_MODELS") or DEFAULT_VALIDATION_MODELS)

    payload = {
        "ideationModels": ideation_models,
        "umlModels": uml_models,
        "validationModels": validation_models,
        "defaultNumCtx": client.num_ctx,
    }

    return {
        "statusCode": 200,
        "headers": cors_headers,
        "body": json.dumps(payload),
    }

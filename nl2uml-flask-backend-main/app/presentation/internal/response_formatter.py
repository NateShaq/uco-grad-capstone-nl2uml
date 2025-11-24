def format_success_response(result: str) -> dict:
    return {
        "statusCode": 200,
        "body": result
    }

def format_error_response(error: str) -> dict:
    return {
        "statusCode": 500,
        "body": f"Internal server error: {error}"
    }

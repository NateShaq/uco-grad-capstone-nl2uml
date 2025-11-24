from typing import Any, Dict, Tuple

# Handlers return (payload, status_code, headers_dict|None)

def get_diagram_handler(service, diagram_id: str) -> Tuple[Any, int, Dict[str, str] | None]:
    # TODO: wire to your repos
    return {"id": diagram_id, "status": "ok"}, 200, None

def create_diagram_handler(service) -> Tuple[Any, int, Dict[str, str] | None]:
    # TODO: use request.get_json() if needed
    return {"status": "created"}, 201, None

def update_diagram_handler(service, diagram_id: str) -> Tuple[Any, int, Dict[str, str] | None]:
    return {"id": diagram_id, "status": "updated"}, 200, None

def delete_diagram_handler(service, diagram_id: str) -> Tuple[Any, int, Dict[str, str] | None]:
    return {"id": diagram_id, "status": "deleted"}, 200, None
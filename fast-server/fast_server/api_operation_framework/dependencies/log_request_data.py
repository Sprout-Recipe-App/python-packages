from datetime import UTC, datetime
import json

from fastapi import Request
from rich.pretty import pretty_repr

from dev_pytopia import Logger

LOGGER = Logger("INFO")


async def log_request_data(request: Request):
    data = {
        "operation": getattr(request.scope.get("route"), "name", "Unknown"),
        "endpoint": str(request.url),
        "method": request.method,
        "timestamp": datetime.now(UTC).isoformat() + "Z",
        "client_ip": getattr(request.client, "host", "Unknown"),
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
    }
    if request.method in {"POST", "PUT", "PATCH"} and (raw := await request.body()):
        data["body"] = json.loads(raw)
    LOGGER.info(f"📝 Received API Request\n{pretty_repr(data, expand_all=True)}")

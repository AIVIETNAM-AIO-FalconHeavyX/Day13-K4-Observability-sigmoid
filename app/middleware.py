from __future__ import annotations

import re
import time
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


_REQUEST_ID_RE = re.compile(r"^req-[0-9a-fA-F]{8}$")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Context vars are task-local, but clearing at the boundary prevents stale
        # values from leaking when a server reuses execution context.
        clear_contextvars()
        requested_id = request.headers.get("x-request-id", "")
        correlation_id = (
            requested_id
            if _REQUEST_ID_RE.fullmatch(requested_id)
            else f"req-{uuid.uuid4().hex[:8]}"
        )
        bind_contextvars(correlation_id=correlation_id)
        request.state.correlation_id = correlation_id

        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            # Return a response here so even unhandled failures carry the same
            # correlation headers as successful requests.
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"},
            )
        finally:
            response.headers["x-request-id"] = correlation_id
            response.headers["x-response-time-ms"] = str(
                round((time.perf_counter() - started) * 1000, 2)
            )
            clear_contextvars()
        return response

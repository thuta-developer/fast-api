import uuid
from collections.abc import Callable
from starlette.types import ASGIApp, Receive, Scope, Send

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Header တွေကို ရှာဖွေခြင်း
        headers = dict(scope.get("headers", []))
        # bytes ကနေ string ပြောင်းပြီး x-request-id ရှိမရှိ စစ်ဆေးခြင်း
        request_id_bytes = headers.get(b"x-request-id")
        request_id = request_id_bytes.decode("utf-8") if request_id_bytes else str(uuid.uuid4())

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = message.setdefault("headers", [])
                headers.append((b"X-Request-ID", request_id.encode("utf-8")))
            await send(message)

        await self.app(scope, receive, send_wrapper)
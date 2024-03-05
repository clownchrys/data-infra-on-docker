from typing import *
import asyncio
import json
import time
from datetime import datetime

from starlette.requests import Request
from starlette.responses import (
    Response,
    StreamingResponse,
    JSONResponse,
)
from starlette.types import (
    Message,
    Scope,
    Receive,
    Send,
)
from starlette.datastructures import Headers
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import (
    FastAPI,
    HTTPException,
    status,
)

from common.logger import AccessLogger


class RequestWithBody(Request):
    def __init__(self, request: Request):
        super().__init__(request.scope, self._receive)
        self._request = request
        self._body_returned = False

    async def _receive(self) -> Message:
        if self._body_returned:
            message = {"type": "http.disconnect"}
        else:
            self._body_returned = True
            message = {"type": "http.request", "body": await self._request.body(), "more_body": False}
        return message


class AtTimeMiddleware(BaseHTTPMiddleware):
    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send
    ):
        assert scope["type"] == "http"

        key = "x-at-time".encode("utf-8")
        value = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f").encode("utf-8")

        new_headers = dict(scope["headers"])
        new_headers[key] = value
        scope["headers"] = [(k, v) for k, v in new_headers.items()]

        await self.app(scope, receive, send)


class TimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: FastAPI,
        timeout: int,
    ):
        super().__init__(app)
        self.app = app
        self.timeout = timeout

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        print(self.__class__.__qualname__)
        return await asyncio.wait_for(call_next(RequestWithBody(request)), timeout=self.timeout)
        # try:
        #     async with timeout(self.timeout):
        #         response = await call_next(RequestWithBody(request))
        #     return response
        # except asyncio.TimeoutError:
        #     raise HTTPException(
        #         status_code=status.HTTP_408_REQUEST_TIMEOUT,
        #         detail="Request timeout"
        #     )


class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        print(self.__class__.__qualname__)
        
        response = await call_next(RequestWithBody(request))
        print(type(response))

        if type(response) == Response:
            resp_body = json.loads((await response.body()).decode("utf-8"))
        elif type(response) == JSONResponse:
            resp_body = json.loads(response.body.decode("utf-8"))
        elif type(response) == StreamingResponse:
            resp_body = " ".join([item.decode("utf-8") async for item in response.body_iterator])
        else:
            raise NotImplementedError(f"response-type: {type(response)}")
        
        log_data = {
            "request": {
                # "url": request.url._url,
                # "url_for": request.url_for, # url_for(self, name: str, **path_params: Any) -> str
                "path": request.url.path,
                "host": request.client.host,
                "method": request.method,
                # "session": request.session, # AssertionError: SessionMiddleware must be installed to access request.session
                # "state": request.state, # <starlette.datastructures.State object at 0x7f750f21b250>
                "headers": dict(request.headers),
                # "cookies": request.cookies, # included in headers
                # "auth": request.auth, # AssertionError: AuthenticationMiddleware must be installed to access request.auth
                "path_params": dict(request.path_params),
                "query_params": dict(request.query_params),
                # "stream": request.stream(), # <async_generator object Request.stream at 0x7f5d1312c670>
                # "user": request.user, # AssertionError: AuthenticationMiddleware must be installed to access request.user
                # "values": request.values(), # ValuesView(<starlette.requests.Request object at 0x7f43e27bf8b0>)
                "body": (await request.body()).decode("utf-8")
            },
            "response": {
                "status_code": response.status_code,
                "body": resp_body
            },
        }
        AccessLogger.info(log_data)

        return Response(
            status_code=response.status_code,
            content=resp_body,
            headers=dict(response.headers),
            media_type=response.media_type,
            background=response.background
        )

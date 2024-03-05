from typing import *
import os
import uuid

import time
import json
import traceback as tb
from datetime import datetime

from fastapi import (
    Request,
    Response,
    BackgroundTasks,
    status,
)
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.routing import APIRoute

from common.logger import AccessLogger, ErrorLogger


class LoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        handler = super().get_route_handler()

        async def wrapper(request: Request) -> Response:
            start_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")
            error_log = None
            start = time.perf_counter()

            try:
                response = await handler(request)
                elapsed = time.perf_counter() - start
            except Exception as error:
                elapsed = time.perf_counter() - start
                response = JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=None
                )
                error_log = await self.error_log(request, error, start_time, elapsed)

            response.background = response.background or BackgroundTasks()
            response.background.add_task(
                func=AccessLogger.info,
                msg=await self.access_log(request, response, start_time, elapsed)
            )
            if error_log:
                response.background.add_task(
                    func=ErrorLogger.error,
                    msg=error_log
                )
            return response

        return wrapper
    
    
    async def access_log(
        self,
        request: Request,
        response: Response,
        start_time: str,
        elapsed: float,
    ) -> dict:
        req_body = json.loads((await request.body()).decode("utf-8"))

        if type(response) == Response:
            resp_body = json.loads((await response.body()).decode("utf-8"))
        elif type(response) == JSONResponse:
            resp_body = json.loads(response.body.decode("utf-8"))
        elif type(response) == StreamingResponse:
            resp_body = None
        else:
            raise NotImplementedError(f"response-type: {type(response)}")

        log_data = {
            "worker_id": os.getpid(),
            "start_time": start_time,
            "elapsed": elapsed,
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
                "body": req_body,
            },
            "response": {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": resp_body,
                "type": str(type(response)),
            },
        }
        return log_data


    async def error_log(
        self,
        request: Request,
        error: Exception,
        start_time: str,
        elapsed: float,
    ) -> dict:
        req_body = (await request.body()).decode("utf-8")

        log_data = {
            "worker_id": os.getpid(),
            "start_time": start_time,
            "elapsed": elapsed,
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
                "body": req_body,
            },
            "error": {
                "type": str(type(error)),
                "message": "".join(tb.format_exception(etype=type(error), value=error, tb=error.__traceback__)),
            },
        }
        return log_data

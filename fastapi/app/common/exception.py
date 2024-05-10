import traceback as tb
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import status, BackgroundTasks
from fastapi.exceptions import ValidationException

from common.logger import ErrorLogger


class APIException(Exception):
    def __init__(self, status_code: int, response: BaseModel):
        """
        response = TestResponse()
        raise APIException(status.HTTP_400_BAD_REQUEST, response)
        """
        assert isinstance(response, BaseModel), "response is not a pydantic model"
        self.status_code = status_code
        self.response = response


class ExceptionHandler:
    @classmethod
    async def APIException(cls, request: Request, exception: APIException):
        ErrorLogger.error({
            "headers": dict(request.headers),
            "error": {
                "type": type(exception).__qualname__,
                "traceback": "".join(tb.format_exception(type(exception), value=exception, tb=exception.__traceback__)),
            }
        })
        response = JSONResponse(
            status_code=exception.status_code,
            content=exception.response.dict(),
        )
        return response
    

    @classmethod
    async def ValidationException(cls, request: Request, exception: ValidationException):
        ErrorLogger.error({
            "headers": dict(request.headers),
            "error": {
                "type": type(exception).__qualname__,
                "traceback": exception.errors(),
            }
        })
        response = JSONResponse(
            status_code=exception.status_code,
            content={"detail": exception.errors(), "body": exception.body},
        )
        return response


    @classmethod
    async def UnhandledException(cls, request: Request, exception: Exception):
        log = {
            "request": {
                "path": request.url.path,
                "host": request.client.host,
                "method": request.method,
                "headers": dict(request.headers),
                "path_params": dict(request.path_params),
                "query_params": dict(request.query_params),
            },
            "error": {
                "type": type(exception).__qualname__,
                "message": "".join(tb.format_exception(type(exception), value=exception, tb=exception.__traceback__)),
            },
        }
        response = JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=None)
        response.background = response.background or BackgroundTasks()
        response.background.add_task(func=ErrorLogger.error, msg=log)
        return response

import traceback as tb
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import (
    status,
    BackgroundTasks,
)
from common.logger import ErrorLogger


# class APIException(Exception):
#     def __init__(self, err_code: int, err_msg: str):
#         self.err_code = err_code
#         self.err_msg = err_msg


class APIException(Exception):
    def __init__(self, response_status_code: int, response_content: dict):
        """
        response = TestResponse()
        raise APIException(status.HTTP_400_BAD_REQUEST, response.dict())
        """
        self.response_status_code = response_status_code
        self.response_content = response_content


class ExceptionHandler:
    @classmethod
    async def APIException(cls, request: Request, exception: APIException):
        response = JSONResponse(
            status_code=exception.response_status_code,
            content=exception.response_content,
        )
        ErrorLogger.error({
            "headers": dict(request.headers),
            "error": {
                "type": type(exception).__qualname__,
                "traceback": "".join(tb.format_exception(type(exception), value=exception, tb=exception.__traceback__)),
            }
        })
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

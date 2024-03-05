import traceback as tb
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import (
    status,
    BackgroundTasks,
)
from common.logger import ErrorLogger


class APIException(Exception):
    def __init__(self, err_code: int, err_msg: str):
        self.err_code = err_code
        self.err_msg = err_msg


class ExceptionHandler:
    @classmethod
    async def unhandled_exception(cls, request: Request, error: Exception):
        """
        Exception Handler 단에서는 Req Body 접근이 불가
        따라서, Req Body에 접근하지 않는다면 좋은 선택지가 되겠으나,
        여기에서는 Req Body까지 로깅하고자 하므로 Route Class를 구현하여 사용함
        대신에 본 핸들러는 미들웨어 디버깅을 위한 Traceback 프린트 기능만 남겨놓음
        """
        print(cls.__qualname__)
        log_data = {
            "request": {
                "path": request.url.path,
                "host": request.client.host,
                "method": request.method,
                "headers": dict(request.headers),
                "path_params": dict(request.path_params),
                "query_params": dict(request.query_params),
            },
            "error": {
                "type": type(error).__qualname__,
                "message": "".join(tb.format_exception(etype=type(error), value=error, tb=error.__traceback__)),
            },
        }
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=log_data
        )
        response.background = response.background or BackgroundTasks()
        response.background.add_task(
            func=ErrorLogger.error,
            msg=log_data,
        )
        return response

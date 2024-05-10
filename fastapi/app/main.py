from typing import *
import os

from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from asgi_correlation_id.middleware import CorrelationIdMiddleware
from starlette_csrf import CSRFMiddleware
from starlette_prometheus import metrics, PrometheusMiddleware

from common.logger import AppLogger
from common.exception import APIException, ExceptionHandler
from common.middleware import (
    TimeoutMiddleware,
    AtTimeMiddleware,
)

from router import (
    common,
    test,
    jk_recom_actvtbased,
)


"""
class FastAPI(starlette.applications.Starlette)

FastAPI(
    *,
    debug: bool = False,
    routes: Union[List[starlette.routing.BaseRoute], NoneType] = None,
    title: str = 'FastAPI',
    description: str = '',
    version: str = '0.1.0',
    openapi_url: Union[str, NoneType] = '/openapi.json',
    openapi_tags: Union[List[Dict[str, Any]], NoneType] = None,
    servers: Union[List[Dict[str, Union[Any, str]]], NoneType] = None,
    dependencies: Union[Sequence[fastapi.params.Depends], NoneType] = None,
    default_response_class: Type[starlette.responses.Response] = <fastapi.datastructures.DefaultPlaceholder object at 0x7f16579e6310>,
    docs_url: Union[str, NoneType] = '/docs',
    redoc_url: Union[str, NoneType] = '/redoc',
    swagger_ui_oauth2_redirect_url: Union[str, NoneType] = '/docs/oauth2-redirect',
    swagger_ui_init_oauth: Union[Dict[str, Any], NoneType] = None,
    middleware: Union[Sequence[starlette.middleware.Middleware], NoneType] = None,
    exception_handlers: Union[Dict[Union[int, Type[Exception]], Callable[[starlette.requests.Request, Any], Coroutine[Any, Any, starlette.responses.Response]]], NoneType] = None,
    on_startup: Union[Sequence[Callable[[], Any]], NoneType] = None,
    on_shutdown: Union[Sequence[Callable[[], Any]], NoneType] = None,
    terms_of_service: Union[str, NoneType] = None,
    contact: Union[Dict[str, Union[Any, str]], NoneType] = None,
    license_info: Union[Dict[str, Union[Any, str]], NoneType] = None,
    openapi_prefix: str = '',
    root_path: str = '',
    root_path_in_servers: bool = True,
    responses: Union[Dict[Union[int, str], Dict[str, Any]], NoneType] = None,
    callbacks: Union[List[starlette.routing.BaseRoute], NoneType] = None,
    deprecated: Union[bool, NoneType] = None,
    include_in_schema: bool = True,
    **extra: Any
) -> None
"""


app = FastAPI(
    middleware=[
        Middleware(TrustedHostMiddleware, allowed_hosts=["*"]),
        Middleware( CORSMiddleware, allow_origins=['*']),
        # Middleware(
        #     CSRFMiddleware,
        #     secret="<CSRF_SECRET>"
        # ),
        Middleware(
            CorrelationIdMiddleware,
            header_name="X-Request-ID",
            update_request_header=True,
            # generator=lambda: uuid4().hex,
            # validator=is_valid_uuid4,
            # transformer=lambda a: a,
        ),
        Middleware(SessionMiddleware, secret_key="<SESSION_SECRET>"),
        Middleware(PrometheusMiddleware),
        Middleware(TimeoutMiddleware, timeout=3),
        Middleware(AtTimeMiddleware)
    ],
    exception_handlers={
        APIException: ExceptionHandler.APIException,
        RequestValidationError: ExceptionHandler.ValidationException,
        ResponseValidationError: ExceptionHandler.ValidationException,
        Exception: ExceptionHandler.UnhandledException,
    }
)

# Routers
app.add_route("/metrics", metrics) # prometheus

app.include_router(common.router)
app.include_router(test.router)
app.include_router(jk_recom_actvtbased.router)

# Lifespan
@app.on_event("startup")
async def on_startup():
    AppLogger.info("server startup")

@app.on_event("shutdown")
async def on_shutdown():
    AppLogger.info("server shutdown")

@app.get("/", response_model_exclude_none=True)
def read_root():
    return {"Hello": "World"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}

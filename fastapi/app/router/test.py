from fastapi import APIRouter
from model.test import TestRequest
from common.route_class import LoggingRoute


router = APIRouter(
    prefix="/test",
    tags=["TEST"],
    route_class=LoggingRoute
)


@router.post("/no_error")
def no_error(body: TestRequest):
    return "True"


@router.post("/error")
def error(body: TestRequest):
    raise Exception("TEST!!")


@router.post("/timeout")
def timeout(body: TestRequest):
    import time
    time.sleep(body.value or 30)

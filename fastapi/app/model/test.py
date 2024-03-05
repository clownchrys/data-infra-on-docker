from typing import *
from pydantic import BaseModel


class TestRequest(BaseModel):
    value: Optional[Any]

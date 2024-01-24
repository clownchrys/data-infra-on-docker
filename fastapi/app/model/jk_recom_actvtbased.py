from typing import List
from pydantic import BaseModel

class _UserParams(BaseModel):
    age: int
    jobtype_code: List[int]

class _GnoRecomMeta(BaseModel):
    gno: int
    min_age: int
    max_age: int
    jobtype_code: List[int]
    # vector: List[float]
    score: float

class ApiInput(BaseModel):
    input_gno: List[int]
    exclude_gno: List[int]
    user: _UserParams
    topk: int

class ApiOutput(BaseModel):
    success: bool
    status_code: int
    result: List[_GnoRecomMeta]

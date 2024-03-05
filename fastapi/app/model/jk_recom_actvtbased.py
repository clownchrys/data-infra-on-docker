from typing import *
from pydantic import BaseModel, Field
from common.util import NumpyArray


################################
#          Sub Models          #
################################


class _KnnApiInputUserMeta(BaseModel):
    age: int
    jobtype_code: List[int] = Field(max_length=5)


class _KnnApiOutputGnoMeta(BaseModel):
    gno: int
    min_age: int
    max_age: int
    jobtype_code: List[int] = Field(max_length=5)
    # vector: List[NumpyArray(dtype="float16", shape=[-1, 3])]
    score: float


class _CsvApiOutputGnoMeta(BaseModel):
    gno: int
    score: float


################################
#          I/O Models          #
################################


class KnnApiInput(BaseModel):
    input_gno: List[int] = Field(max_length=10)
    exclude_gno: List[int] = Field(max_length=100)
    user: _KnnApiInputUserMeta
    topk: int
    threshold: Optional[float]


class KnnApiOutput(BaseModel):
    success: bool
    status_code: int
    result: List[_KnnApiOutputGnoMeta]


class CsvApiInput(BaseModel):
    input_gno: List[int] = Field(max_length=10)
    exclude_gno: List[int] = Field(max_length=100)
    topk: int = 100
    threshold: float = 0.0


class CsvApiOutput(BaseModel):
    success: bool
    status_code: int
    result: List[_CsvApiOutputGnoMeta]

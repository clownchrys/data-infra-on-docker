from fastapi import Request, APIRouter
from fastapi.app.common.enum import ApiEnvEnum

from model.jk_recom_actvtbased import (
    KnnApiInput, KnnApiOutput, _KnnApiOutputGnoMeta,
    CsvApiInput, CsvApiOutput, _CsvApiOutputGnoMeta,
)
from external.elasticsearch import client as es
from common.route_class import LoggingRoute
from common.decorator import use_mockup


"""
class APIRouter(starlette.routing.Router)

APIRouter(
    *,
    prefix: str = '',
    tags: Union[List[str], NoneType] = None,
    dependencies: Union[Sequence[fastapi.params.Depends], NoneType] = None,
    default_response_class: Type[starlette.responses.Response] = <fastapi.datastructures.DefaultPlaceholder object at 0x7efcf17a7cd0>,
    responses: Union[Dict[Union[int, str], Dict[str, Any]], NoneType] = None,
    callbacks: Union[List[starlette.routing.BaseRoute], NoneType] = None,
    routes: Union[List[starlette.routing.BaseRoute], NoneType] = None,
    redirect_slashes: bool = True,
    default: Union[Callable[[MutableMapping[str, Any], Callable[[], Awaitable[MutableMapping[str, Any]]], Callable[[MutableMapping[str, Any]], Awaitable[NoneType]]], Awaitable[NoneType]], NoneType] = None,
    dependency_overrides_provider: Union[Any, NoneType] = None,
    route_class: Type[fastapi.routing.APIRoute] = <class 'fastapi.routing.APIRoute'>,
    on_startup: Union[Sequence[Callable[[], Any]], NoneType] = None,
    on_shutdown: Union[Sequence[Callable[[], Any]], NoneType] = None,
    deprecated: Union[bool, NoneType] = None,
    include_in_schema: bool = True
) -> None
"""


router = APIRouter(
    prefix="/recommend/actvtbased",
    tags=["Jobkorea Recommend"],
    route_class=LoggingRoute,
)


"""
Help on method get in module fastapi.routing:

get(
    path: str,
    *,
    response_model: Union[Type[Any], NoneType] = None,
    status_code: Union[int,NoneType] = None,
    tags: Union[List[str], NoneType] = None,
    dependencies: Union[Sequence[fastapi.params.Depends], NoneType] = None,
    summary: Union[str, NoneType] = None,
    description: Union[str, NoneType] = None,
    response_description: str = 'Successful Response',
    responses: Union[Dict[Union[int, str], Dict[str, Any]], NoneType] = None,
    deprecated: Union[bool, NoneType] = None,
    operation_id: Union[str, NoneType] = None,
    response_model_include: Union[Set[Union[int, str]], Dict[Union[int, str], Any], NoneType] = None,
    response_model_exclude: Union[Set[Union[int, str]], Dict[Union[int, str], Any], NoneType] = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False, include_in_schema: bool = True,
    response_class: Type[starlette.responses.Response] = <fastapi.datastructures.DefaultPlaceholder object at 0x7fa163028910>,
    name: Union[str, NoneType] = None,
    callbacks: Union[List[starlette.routing.BaseRoute], NoneType] = None,
    openapi_extra: Union[Dict[str, Any], NoneType] = None
) -> Callable[[~DecoratedCallable], ~DecoratedCallable]

method of fastapi.routing.APIRouter instance
"""


@router.post(
    path="/recommend_with_knn",
    response_model=KnnApiOutput,
    description="온라인 ann을 활용한 추천 API",
    deprecated=True,
)
def recommend_with_knn(body: KnnApiInput, req: Request):
    INDEX_NAME = "gno_properties"
    VECTOR_FIELD = "vector"

    # query 1: Get Gno Vector
    resp = es.search(
        index=INDEX_NAME,
        query={"bool": {"must": [{"terms": {"gno": body.input_gno}}]}},
        source_includes=["gno", VECTOR_FIELD]
    )
    input_docs = [obj["_source"] for obj in resp.body["hits"]["hits"]]

    # query 2: Search to recommend
    knn_boost = 0.7
    knn_base = {
        "field": VECTOR_FIELD,
        # "query_vector": query_vector,
        "k": 100,
        "num_candidates": 1000,
        "filter": {
            "bool" : {
                "must_not": [
                    {"terms": {"gno": body.input_gno + body.exclude_gno}}
                ],
                "filter": [
                    {"range": {"min_age": {"lte": body.user.age}}},
                    {"range": {"max_age": {"gte": body.user.age}}},
                    # {"terms": {"jobtype_code": user["jobtype"]}}
                ]
            }
        },
        # "boost": 0.6,
    }
    knn = [
        {
            **knn_base,
            "query_vector": doc[VECTOR_FIELD],
            "boost": knn_boost / len(input_docs)
        }
        for doc in input_docs
    ]
    query = {
        "bool": {
            "should": [
                {"term": {"jobtype_code": {"value": v, "boost": (1 - knn_boost) / len(body.user.jobtype_code)}}}
                for v in body.user.jobtype_code
            ]
        }
    }
    resp = es.search(
        index=INDEX_NAME,
        query=query,
        knn=knn,
        size=body.topk,
        source_excludes=[VECTOR_FIELD],
        min_score=body.threshold,
        # rank={"rrf": {}}  # payed version only
    )

    # post-processing to respond
    response = KnnApiOutput(
        success=True,
        status_code=200,
        result=[
            _KnnApiOutputGnoMeta(
                gno=obj["_source"]["gno"],
                min_age=obj["_source"]["min_age"],
                max_age=obj["_source"]["max_age"],
                jobtype_code=obj["_source"]["jobtype_code"],
                score=obj["_score"],
            )
            for obj in resp["hits"]["hits"]
        ]
    )
    return response


@router.post(
    path="/recommend_with_csv",
    response_model=CsvApiOutput,
    description="사전 계산된 csv을 활용한 추천 API",
    response_description="추천 공고 및 스코어",
    responses={
        201: {
            "description": "The item was not found",
            "model": CsvApiOutput,
        },
        202: {
            "description": "Item requested by ID",
            "content": {
                "application/json": {
                    "example": {"id": "bar", "value": "The bar tenders"}
                }
            },
        },
        203: {
            "description": "Additional Response",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/KnnApiOutput"
                    }
                }
            }
        },
    },
    deprecated=False,
)
@use_mockup(
    return_value=CsvApiOutput(
        success=True,
        status_code=200,
        result=[
            _CsvApiOutputGnoMeta(gno=1, score=0.76),
            _CsvApiOutputGnoMeta(gno=2, score=0.50),
        ]
    ),
    target=[ApiEnvEnum.DEV]
)
def recommend_with_csv(body: CsvApiInput, req: Request) -> CsvApiOutput:
    INDEX_NAME = "jk_recom_actvtbased"

    # query 1. search to recommend
    query = {
        "bool": {
            "filter": [
                {"terms": {"gno": body.input_gno}},
                {"range": {"score": {"gte": body.threshold or 0.0}}},
            ],
            "must_not": [
                {"terms": {"gno_similar": body.exclude_gno}},
            ]
        }
    }
    aggs = {
        "groupby": {
            "terms": {
                "field": "gno_similar",
                "order": {"sum_score": "desc"},
                "size": body.topk
            },
            "aggs": {
                "sum_score": {"sum": {"field": "score"}}
            }
        }
    }
    resp = es.search(
        index=INDEX_NAME,
        query=query,
        aggs=aggs,
        source=False,
        size=0
    )

    # post-processing to respond
    response = CsvApiOutput(
        success=True,
        status_code=200,
        result= [
            _CsvApiOutputGnoMeta(
                gno=obj["key"],
                score=obj["sum_score"]["value"]
            )
            for obj in resp["aggregations"]["groupby"]["buckets"]
        ]
    )
    return response

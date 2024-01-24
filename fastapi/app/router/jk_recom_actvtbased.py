from fastapi import APIRouter, Request
from model.jk_recom_actvtbased import ApiInput, ApiOutput, _GnoRecomMeta
from external.elasticsearch import client as es_client

router = APIRouter(
    prefix="/recommend/actvtbased",
    tags=["JK", "Recom", "Actvtbased"],
)

@router.post("/")
def do_recommend(body: ApiInput, req: Request):
    vector_index = "gno_properties"

    # query 1: Get Gno Vector
    resp = es_client.search(
        index=vector_index,
        query={"bool": {"must": [{"terms": {"gno": body.input_gno}}]}},
        source_includes=["gno", "vector"]
    )
    input_docs = [obj["_source"] for obj in resp.body["hits"]["hits"]]

    # query 2: Search to recommend
    knn_boost = 0.7
    knn_base = {
        "field": "vector",
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
            "query_vector": doc["vector"],
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
    resp = es_client.search(
        index=vector_index,
        query=query,
        knn=knn,
        size=body.topk,
        source_excludes=["vector"]
        # rank={"rrf": {}}  # payed version only
    )

    # post-processing to respond
    response = ApiOutput(
        success=True,
        status_code=200,
        result=[
            _GnoRecomMeta(
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

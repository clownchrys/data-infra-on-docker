import numpy as np  # or torch
import json
from enum import Enum


class ESWriteOperation(str, Enum):
    INDEX = "index"
    UPSERT = "upsert"


def main():
    # parameters
    primary_key = "gno"
    serving_op = ESWriteOperation.INDEX.value
    embedding_path = "s3://test/example/MF.jit.pt"
    index_path = "s3://test/example/MF.index2item.json"
    # feature_table_path = "path.to.table"

    # get all tables
    embedding_table = generate_embedding_table(
        spark,
        primary_key=primary_key,
        embedding_path=embedding_path,
        index_path=index_path,
    )
    # feature_table = spark.read.table(feature_table_path)

    # add features to search
    # transformed_df = embedding_table.join(feature_table, primary_key, "inner")

    # serve into es
    es_opts = {
        "es.nodes": "http://elasticsearch:9200",
        "es.nodes.wan.only": "true",
        "es.net.ssl": "true",
        "es.http.timeout": "10m",
        # "es.net.http.auth.user": "<USERNAME>",
        # "es.net.http.auth.pass": "<PASSWORD>",
        "es.resource": "<INDEX_NAME>",
    }

    if (serving_op == ESWriteOperation.INDEX):
        es_opts["es.write.operation"] = "index"
        es_opts["mode"] = "overwrite"

    elif (serving_op == ESWriteOperation.UPSERT):
        es_opts["es.write.operation"] = "upsert"
        # es_opts["es.mapping.id"] = "<MAPPING_ID>"
        es_opts["es.update.retry.on.conflict"] = "3"
        es_opts["mode"] = "append"

    else:
        raise NotImplementedError(f"operation {serving_op!r} is not implemented!")

    # transformed_df.write.format("org.elasticsearch.spark.sql").options(**es_opts).save()
    embedding_table.write.format("org.elasticsearch.spark.sql").options(**es_opts).save()


def generate_embedding_table(spark, primary_key: str, embedding_path: str, index_path: str):
    embedding = np.load(embedding_path)
    with open(index_path, "r") as f:
        index2sth = {int(k): v for k, v in json.load(f)}
    rows = [{primary_key: index2sth[i], "vector": embedding[i].tolist()} for i in index2sth.keys()]
    return spark.createDataFrame(rows)

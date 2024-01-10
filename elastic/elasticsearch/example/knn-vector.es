GET _search
{
  "query": {
    "match_all": {}
  }
}

DELETE /vector-index

PUT /vector-index
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
   "mappings": {
    "properties": {
      "name": {
        "type": "keyword"
      },
      "vector": {
        "type": "dense_vector",
        "dims": 2,
        "index": true,
        "similarity": "cosine"
      }
    }
  }
}

GET /vector-index/_search
{
  "query": {
    "script_score": {
      "query": {"match_all": {}},
      "script": {
        "source": "cosineSimilarity(params.inputVector, 'vector') + 1.0",
        "params": {"inputVector": [0.1,0.1]}
      }
    }
  },
  "size": 10
}

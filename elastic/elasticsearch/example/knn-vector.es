GET _cluster/health?pretty

/* vector-index */

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

/* gno_properties */

POST /gno_properties/_count?pretty

// Usage of function_score with knn
GET /gno_properties/_search?include_named_queries_score
{
  "query": {
    "function_score": {
      "query": {
        "bool": {
          "minimum_should_match": 0,
          "must": [
            {"match_all": {"_name": "match_all", "boost": 0.1}}
          ], 
          "should": [
            {"match": {"gno": {"_name": "match_1", "query": 77542, "boost": 1}}},
            {"match": {"gno": {"_name": "match_2", "query": 77542, "boost": 1}}}
          ]
        }
      }, 
      "functions": [
        {
          "filter": {"match": {"gno": {"query": 77542, "_name": "function_1"}}},
          "weight": 1.0
        },
        {
          "filter": {"match": {"gno": {"query": 77542, "_name": "function_2"}}},
          "weight": 0.5
        }
      ],
      "score_mode": "max",
      "boost_mode": "avg",
      "max_boost": 1,
      "boost": 0.5
    }
  },
  "knn": {
    "field": "vector", 
    "query_vector": [
      1, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0
    ],
    "k": 10,
    "num_candidates": 100,
    "boost": 0.5
  },
  "_source": ["gno"],
  "min_score": 0.5
}

// Usage of query_string
GET /gno_properties/_search
{
  "query": {
    "query_string": {
      "default_field": "jobtype_code",
      "query": "1 OR 2",
      "boost": 0.5
    }
  }
}

// Usage of painless script
GET /gno_properties/_search?include_named_queries_score
{
  "query": {
    "bool": {
      "should": [
        {"range": {"gno": {"gte": 5, "lte": 10, "_name": "should_range_gno_0_10"}}},
        {"range": {"gno": {"gte": 11, "lte": 20, "_name": "should_gno_range_11_20"}}},
        
        //{"range": {"gno": {"gt": 0, "lte": 5}}},
        {
          "script": {
            "script": "(0 < doc['gno'].getValue()) && (doc['gno'].getValue() <= 5)",
            "_name": "should_script_1"
          }
        },
        
        //{"terms": {"jobtype_code": [1, 2], "_name": "should_terms_jobtype_code_1_2"}},
        {
          "script": {
            "script": {
              "source": "doc['jobtype_code'].contains(1L) || doc['jobtype_code'].contains(2L)",
              "lang": "painless"
            },
            "_name": "should_script_2"
          }
        },
        
        // test
        {
          "script": {
            "script": {
              "source": """
                int castToIntFromLong(long v) { return (int) v; }
                int gno = castToIntFromLong(doc['gno'].value);
                if (gno < 3) { return true; }
                else { return false; }
              """,
              "lang": "painless"
            },
            "_name": "multi_line_script"
          }
        }
      ], 
      "filter": {
        "terms": {
          "jobtype_code": [1, 2],
          "_name": "filter_terms_jobtype_code_1_2"
        }
      },
      "boost": 1.0
    }
  },
  "script_fields": {
    "test": {
      "script": "return 1"
    }
  }, 
  "_source": ["gno", "jobtype_code"]
}

// Usage of query sql
GET _sql?format=txt
{
  "query": "SELECT gno, vector FROM gno_properties"
}

DELETE /gno_properties

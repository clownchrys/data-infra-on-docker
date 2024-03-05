GET jk_story_user/_search
GET jk_story_master/_search
GET _cat/aliases



GET api_data_test/_alias
GET api_data_test/_count
GET api_data_test/_search



# 1. query 절에 들어가는 value 값들은 모두 request 값을 받아서 사용함
# 2. job_type_code 가 조회되지 않아, must_not 쿼리에 gno 사용함
# 3. df_to_es 사용 시, 전체 row 가 다 들어가지 않음
GET api_data_test/_search
{
  "size": 0,
  
  "query": {
    "bool": {
      "filter": [
        {"terms": {"gno": [39279118, 38826054, 38817484]}},
        {"terms": {"gender_type_code": [0, 2]}},
        {"range": {"edu_level_code": {"lte": 4}}},
        {"range": {"age_limit_under": {"lte": 20}}},
        {"range": {"age_limit_over": {"gte": 20}}},
        {
          "bool": {
            "should": [
              {
                "bool": {
                  "filter": [
                    {"script": {"script": "0 == 0"}},
                    {"terms": {"career_type_code": [1, 3]}}
                  ]
                }
              },
              {
                "bool": {
                  "filter": [
                    {"script": {"script": "0 < 1 && 1 < 3"}},
                    {"terms": {"career_type_code": [1, 2, 3]}},
                    {"range": {"career_year_cnt": {"lte": 1}}}
                  ]
                }
              },
              {
                "bool": {
                  "filter": [
                    {"script": {"script": "3 <= 4"}},
                    {"terms": {"career_type_code": [2, 3]}},
                    {"range": {"career_year_cnt": {"lte": 4}}}
                  ]
                }
              },
              {"match": {"career_type_code": 4}}
            ]
          }
        }
      ],
      "must_not": [
        {"terms": {"job_type_code": [4, 5, 8]}}
      ]
    }
  }, 
  
  "aggs": {
    "result": {
      "terms": {
        "field": "gno_similar",
        "order": {
          "criterion": "desc"
        },
        "size": 100
      },
      "aggs": {
        "criterion": {
          "sum": {
            "field": "score"
          }
        }
      }
    }
  }
}


# Search Template
PUT _scripts/search-jk-recom-renewal
{
  "script": {
    "lang": "mustache",
    "source": """
    {
      "size": 0,
      
      "query": {
        "bool": {
          "filter": [
            {"terms": {"gno": {{#toJson}}input_gnos{{/toJson}}}},
            {"terms": {"gender_type_code": [{{gender_type_code}}, 2]}},
            {"range": {"edu_level_code": {"lte": {{edu_level_code}}}}},
            {"range": {"age_limit_under": {"lte": {{age}}}}},
            {"range": {"age_limit_over": {"gte": {{age}}}}},
            {
              "bool": {
                "should": [
                  {
                    "bool": {
                      "filter": [
                        {"script": {"script": "0 == {{career_year_cnt}}"}},
                        {"terms": {"career_type_code": [1, 3]}}
                      ]
                    }
                  },
                  {
                    "bool": {
                      "filter": [
                        {"script": {"script": "0 < {{career_year_cnt}} && {{career_year_cnt}} < 3"}},
                        {"terms": {"career_type_code": [1, 2, 3]}},
                        {"range": {"career_year_cnt": {"lte": 1}}}
                      ]
                    }
                  },
                  {
                    "bool": {
                      "filter": [
                        {"script": {"script": "3 <= {{career_year_cnt}}"}},
                        {"terms": {"career_type_code": [2, 3]}},
                        {"range": {"career_year_cnt": {"lte": 4}}}
                      ]
                    }
                  },
                  {"match": {"career_type_code": 4}}
                ]
              }
            }
          ],
          "must_not": [
            {"terms": {"job_type_code": {{#toJson}}exclude_job_type_codes{{/toJson}}}}
          ]
        }
      }, 
      
      "aggs": {
        "result": {
          "terms": {
            "field": "gno_similar",
            "order": {
              "criterion": "desc"
            },
            "size": {{limit}}{{^limit}}100{{/limit}}
          },
          "aggs": {
            "criterion": {
              "sum": {
                "field": "score"
              }
            }
          }
        }
      }
    }
    """
  }
}

POST _render/template
{
  "id": "search-jk-recom-renewal",
  "params": {
    "input_gnos": [39279118, 38826054, 38817484],
    "gender_type_code": 0,
    "edu_level_code": 4,
    "age": 20,
    "career_year_cnt": 1,
    "exclude_job_type_codes": [4, 5, 8]
  }
}

GET api_data_test/_search/template
{
  "id": "search-jk-recom-renewal",
  "params": {
    "input_gnos": [39279118, 38826054, 38817484],
    "gender_type_code": 0,
    "edu_level_code": 4,
    "age": 20,
    "career_year_cnt": 1,
    "exclude_job_type_codes": [4, 5, 8]
  }
}
# limit 값은 Optional (기본값: 100)




POST _render/template
{
  "source": """
  {
    "value": {{#toJson}}dic.a{{/toJson}},
    "condition": {{#crit}}1{{/crit}} {{^crit}}-1{{/crit}}
  }
  """,
  "params": {
    "dic": {"a": 1},
    "crit": true
  }
}


GET _cluster/state/?filter_path=metadata.stored_scripts&format=yaml
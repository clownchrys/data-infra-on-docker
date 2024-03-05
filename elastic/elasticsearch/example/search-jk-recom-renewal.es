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
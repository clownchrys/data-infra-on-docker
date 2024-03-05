# step1. m_id (input) -> user_profile
GET es_user_profile/_search
{
  "size": 1,
  "query": {
    "match": {
      "m_id": "20120444"
    }
  }
}

# step2. input_gno (input) + user_profile -> result
GET api_data_test/_search/template
{
  "id": "search_jk_recom_renewal_v1",
  "params": {
    "input_gno": [39279118, 38826054, 38817484],
    
    "gender_type_code": 1,
    "age": 41,
    "career_year_cnt": 1,
    "edu_level_code": [0],
    "exclude_job_type": [8]
  }
}
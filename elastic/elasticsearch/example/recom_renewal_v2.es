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

# step2. user_profile -> matched_gno
GET es_gno_profile/_search/template
{
  "id": "search_available_gno",
  "params": {
    "gender_type_code": 1,
    "age": 41,
    "career_year_cnt": 0,
    "edu_level_code": [0],
    "exclude_job_type": [8]
  }
}

# step3. input_gno (input) + matched_gno -> result
GET api_data_test/_search/template
{
  "id": "search_jk_recom_renewal_v2",
  "params": {
    "input_gno": [39279118, 38826054, 38817484],
    "available_gno": [
      39454400, 39410368, 39310744,
      40001234, 39410369
    ]
  }
}
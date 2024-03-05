# step1. m_id (input) -> user_profile + story_numbers
GET jk_story_user/_search
{
  "size": 1,
  "query": {
    "match": {
      "m_id": "throat"
    }
  }
}

# step2. user_profile + story_number -> result
# 공고형, 통계형 모두 동일한 포맷으로 쿼리

# (공고형) 
GET jk_recm_story_45/_search/template
{
  "id": "search_jk_story_recom",
  "params": {
    "m_id" : "throat",
    "story_number" : "45",
    "jk_jobtitle_code" : 1000112,
    "C_jk_jobtitle_code" : "1000112",
    "segmentation" : 0
  }
}

# (통계형)
GET jk_recm_story_79/_search/template
{
  "id": "search_jk_story_recom",
  "params": {
    "m_id" : "throat",
    "story_number" : "79",
    "jk_jobtitle_code" : 1000112,
    "C_jk_jobtitle_code" : "1000112",
    "segmentation" : 0
  }
}
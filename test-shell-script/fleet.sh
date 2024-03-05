#!/bin/bash

# Make policy for elastic-agent
curl -XPOST kibana:5601/api/fleet/agent_policies?sys_monitoring=true \
-H 'Accept: */*' \
-H 'Cache-Control: no-cache' \
-H 'Connection: keep-alive' \
-H 'Content-Type: application/json' \
-H 'kbn-xsrf: true' \
-u 'elasticadmin:elasticadmin' \
-d '{
  "name": "AGENT_POLICY_01",
  "description": "AGENT_POLICY_01",
  "namespace": "default",
  "monitoring_enabled": ["logs", "metrics"]
}'

# Make token for elascit-agent
POLICY_ID=$(curl -XGET -s kibana:5601/api/fleet/agent_policies -u elasticadmin:elasticadmin | jq .items[] | jq 'select(.name == "AGENT_POLICY_01")' | jq .id)
curl -XPOST kibana:5601/api/fleet/enrollment_api_keys \
-H 'Accept: */*' \
-H 'Cache-Control: no-cache' \
-H 'Connection: keep-alive' \
-H 'Content-Type: application/json' \
-H 'kbn-xsrf: true' \
-u 'elasticadmin:elasticadmin' \
-d '{
  "name": "ELASTIC_AGENT_TOKEN",
  "policy_id": '$POLICY_ID'
}'
MODEL_NAME=testmodel

.PHONY: config
config:
	curl -v localhost:8000/v2/models/${MODEL_NAME}/config | jq

.PHONY: index
index:
	curl -v -XPOST localhost:8000/v2/repository/index | jq

.PHONY: load
load:
	curl -v -XPOST localhost:8000/v2/repository/models/${MODEL_NAME}/load
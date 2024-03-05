#!/bin/bash

# run inference
curl -v -XPOST localhost:8000/v2/models/testmodel/infer -d @body.json | jq
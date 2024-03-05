#!/bin/bash

# bentoml serve service_with_script:service --api-workers 2
# bentoml serve service_with_class:Service

# use bentofile.yaml
bentoml serve --host 0.0.0.0 --port 3000
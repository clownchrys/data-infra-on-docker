#!/bin/bash

MODEL_ARTIFACTS=/tmp/model-artifacts

mkdir -p ${MODEL_ARTIFACTS}
python model.py --artifact-dir ${MODEL_ARTIFACTS}

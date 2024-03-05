#!/bin/bash

MODEL_NAME=testmodel
MODEL_VERSION=5
MODEL_STORE_DIR=/model-store/${MODEL_NAME}

mkdir -pv ${MODEL_STORE_DIR}/${MODEL_VERSION}
echo ${MODEL_STORE_DIR}/${MODEL_VERSION}

python model.py --model-store ${MODEL_STORE_DIR}/${MODEL_VERSION}
cp -rvf config.pbtxt ${MODEL_STORE_DIR}/

# config.pbtxt
# https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/model_configuration.html
# https://github.com/triton-inference-server/common/blob/main/protobuf/model_config.proto

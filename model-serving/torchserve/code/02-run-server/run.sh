#!/bin/bash

# usage: torchserve [-h] [-v | --start | --stop] [--ts-config TS_CONFIG] [--model-store MODEL_STORE] [--workflow-store WORKFLOW_STORE] [--models MODEL_PATH1 MODEL_NAME=MODEL_PATH2... [MODEL_PATH1 MODEL_NAME=MODEL_PATH2... ...]] [--log-config LOG_CONFIG]
#                   [--foreground] [--no-config-snapshots] [--plugins-path PLUGINS_PATH]

# Torchserve

# optional arguments:
#   -h, --help            show this help message and exit
#   -v, --version         Return TorchServe Version
#   --start               Start the model-server
#   --stop                Stop the model-server
#   --ts-config TS_CONFIG
#                         Configuration file for model server
#   --model-store MODEL_STORE
#                         Model store location from where local or default models can be loaded
#   --workflow-store WORKFLOW_STORE
#                         Workflow store location from where local or default workflows can be loaded
#   --models MODEL_PATH1 MODEL_NAME=MODEL_PATH2... [MODEL_PATH1 MODEL_NAME=MODEL_PATH2... ...]
#                         Models to be loaded using [model_name=]model_location format. Location can be a HTTP URL or a model archive file in MODEL_STORE.
#   --log-config LOG_CONFIG
#                         Log4j configuration file for model server
#   --foreground          Run the model server in foreground. If this option is disabled, the model server will run in the background. In combination with --stop the program wait for the model server to terminate.
#   --no-config-snapshots, --ncs
#                         Prevents to server from storing config snapshot files.
#   --plugins-path PLUGINS_PATH, --ppath PLUGINS_PATH
#                         plugin jars to be included in torchserve class path

# Envvars

# JAVA_HOME
# PYTHONPATH
# TS_CONFIG_FILE
# LOG_LOCATION
# METRICS_LOCATION

LOG_LOCATION=/data/ts-log \
torchserve \
--start \
--ncs \
--ts-config config.properties \
--log-config log4j.xml \
--model-store ${MODEL_STORE} \
--models all \
--foreground
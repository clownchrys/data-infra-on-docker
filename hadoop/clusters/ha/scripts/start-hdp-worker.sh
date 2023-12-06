#!/bin/sh

# vcore: 32
# vmem: 128G
# vdisk: os 100G, data1 2T, data2 2T

# start datanode (hdfs)
hdfs --daemon start datanode

# start nodemanager (yarn)
yarn --daemon start nodemanager

# start spark
start-worker.sh

# logging for container-liveness
tail -F ${HADOOP_HOME}/logs/*.log
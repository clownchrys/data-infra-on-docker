#!/bin/sh

# vcore: 8
# vmem: 32G
# vdisk: os 100G, data 500G

# start journalnode (hadoop)
hdfs --daemon start journalnode || exit 1

# start jobhistoryserver (hadoop)
mapred --daemon start historyserver || exit 1

# start balancer (hdfs)
hdfs --daemon start balancer -asService || exit 1

# start sparkhistoryserver (spark)
start-history-server.sh || exit 1

# logging for container-liveness
tail -F ${HADOOP_HOME}/logs/*.log
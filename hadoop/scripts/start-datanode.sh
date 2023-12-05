#!/bin/sh

hdfs --daemon start datanode

# if [ "$JOURNAL_NODE" = "1" ]; then
#   hdfs --daemon start journalnode
# fi

if [ "$BALANCER_NODE" = "1" ]; then
  hdfs --daemon start balancer -asService
fi

# logging for container-liveness
tail -F ${HADOOP_HOME}/logs/*
#!/bin/sh

# start JournalNode
hdfs --daemon start journalnode

# start NameNode
if [ "$ACTIVE_NN" = '1' ]; then
  hdfs namenode -format -force -nonInteractive
else
  sleep 30 && \
  hdfs namenode -bootstrapStandby -force -nonInteractive # for standby nn: copy metadata from active nn
fi

hdfs --daemon start namenode

# start yarn
if [ "$ACTIVE_NN" = '1' ]; then
  start-yarn.sh
else
  yarn --daemon start resourcemanager
fi

# start DFSZKFailoverController
if [ "$ACTIVE_NN" = '1' ]; then
  hdfs zkfc -formatZK -force -nonInteractive
fi
# hdfs --daemon start zkfc

# start JobHistoryServer
mapred --daemon start historyserver

# logging for container-liveness
tail -F ${HADOOP_HOME}/logs/*
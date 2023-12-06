#!/bin/sh

# vcore: 16
# vmem: 128G
# vdisk: os 100G, data 500G
# per instance

NN_MODE=$1

if [ "$NN_MODE" != 'active' ] && [ "$NN_MODE" != 'standby' ]; then
  echo '$NN_MODE should be one of [active, standby], not '"$NN_MODE";
  exit 1;
fi

# start journalnode (hadoop)
hdfs --daemon start journalnode || exit 1

# start resourcemanager (yarn)
# start-yarn.sh
yarn --daemon start resourcemanager

# start namenode (hdfs)
if [ "$NN_MODE" = 'active' ]; then
  # for active nn: formatting namenode
  hdfs namenode -format -force -nonInteractive || exit 1
else
  # for standby nn: copy metadata from active nn
  while ! hdfs namenode -bootstrapStandby -force -nonInteractive;
  do
    echo "waiting 10s for namenode bootstraping..."; sleep 10;
  done
fi
hdfs --daemon start namenode || exit 1

# start DFSZKFailoverController (hdfs)
if [ "$NN_MODE" = 'active' ]; then
  hdfs zkfc -formatZK -force -nonInteractive || exit 1
fi
hdfs --daemon start zkfc || exit 1

# start spark
# echo "[NOT_IMPLEMENTED] SparkApplication"
start-master.sh

# logging for container-liveness
tail -F ${HADOOP_HOME}/logs/*.log
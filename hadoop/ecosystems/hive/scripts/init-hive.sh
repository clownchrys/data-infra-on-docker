#!/bin/sh

# vcore: 4
# vmem: 32G
# vdisk: os 100G, data 500G

# init hive metastore
while ! hive --service schematool -dbType mysql -initSchema;
# When schema upgrade: hive --service schematool -dbType mysql -upgradeSchema
do
    echo "waiting 10s to initialize metastore schema..."
    sleep 10
done

while ! hdfs dfs -ls /;
do
    echo "waiting 10s for connecting to HDFS..."
    sleep 10
done
echo "HDFS Connected successfully"

# tmp directory: Hive process의 중간 데이터 결과를 저장
# warehouse directory
init-hive-dfs.sh || exit 1

# start hive server
# https://coffeedjimmy.github.io/hive/2019/07/25/hive01/

# >/dev/null 2>&1은 stdout을 /dev/null로, stderr를 stdout으로 리디렉션하는 것을 의미
# hive --service metastore > /dev/null 2>&1 &
hive --service metastore -p 9083 -v > /tmp/$(whoami)/metastore.log 2>&1 &
hive --service hiveserver2 --hiveconf hive.server2.thrift.port=10000 > /tmp/$(whoami)/hiveserver2.log 2>&1 &

# CLI test
# STANDALONE_URL=jdbc:hive2://localhost:10000
# ZOOKEEPER_HA_URL=jdbc:hive2://zk-1:2181,zk-2:2181,zk-3:2181/;serviceDiscoveryMode=zooKeeper;zooKeeperNamespace=hiveserver2
# beeline -u $SOME_URL -n <username> -p <password>

# logging for container-liveness
tail -F /tmp/"$(whoami)"/*.log
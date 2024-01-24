SHELL = /bin/zsh
ARCH = $(shell arch)
PROJECT_NAME = data-infra


###############################
#          VARIABLES          #
###############################


# Versions
HADOOP_VERSION = 3.3.6
# SPARK_VERSION = 3.1.2
# SPARK_HADOOP_VERSION = 3.2
SPARK_VERSION = 3.4.2
SPARK_HADOOP_VERSION = 3
SPARK_SCALA_VERSION=2.12
HIVE_VERSION = 3.1.3
KAFKA_VERSION = 2.7.2
KAFKA_SCALA_VERSION = 2.13
ES_VERSION = 8.12.0

# Hadoop
ifneq (${ARCH}, $(filter ${ARCH}, arm64 aarch64))
	HADOOP_BIN_URI = https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz
else
	HADOOP_BIN_URI = https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}-aarch64.tar.gz
endif

# Spark
SPARK_BIN_URI = https://dlcdn.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${SPARK_HADOOP_VERSION}.tgz
# SPARK_BIN_URI = https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${SPARK_HADOOP_VERSION}.tgz
SPARK_DELTA_CORE_JAR_URI = https://repo1.maven.org/maven2/io/delta/delta-core_2.12/2.4.0/delta-core_2.12-2.4.0.jar
SPARK_DELTA_STORAGE_JAR_URI = https://repo1.maven.org/maven2/io/delta/delta-storage/2.4.0/delta-storage-2.4.0.jar
SPARK_MSSQL_JDBC_CONNECTOR_URI = https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/12.4.2.jre8/mssql-jdbc-12.4.2.jre8.jar
SPARK_MSSQL_CONNECTOR_FOR_SPARK_3_1_URI = https://repo1.maven.org/maven2/com/microsoft/azure/spark-mssql-connector_2.12/1.2.0/spark-mssql-connector_2.12-1.2.0.jar
SPARK_MSSQL_CONNECTOR_FOR_SPARK_3_4_URI = https://github.com/microsoft/sql-spark-connector/releases/download/v1.4.0/spark-mssql-connector_2.12-1.4.0-BETA.jar
SPARK_ES_CONNECTOR_JAR_URI = https://repo1.maven.org/maven2/org/elasticsearch/elasticsearch-spark-30_${SPARK_SCALA_VERSION}/${ES_VERSION}/elasticsearch-spark-30_${SPARK_SCALA_VERSION}-${ES_VERSION}.jar 

# Hive
HIVE_BIN_URI = https://dlcdn.apache.org/hive/hive-${HIVE_VERSION}/apache-hive-${HIVE_VERSION}-bin.tar.gz
HIVE_MYSQL_CONNECTOR_URI = https://repo1.maven.org/maven2/mysql/mysql-connector-java/5.1.46/mysql-connector-java-5.1.46.jar
HIVE_GUAVA_JAR_URI = https://repo1.maven.org/maven2/com/google/guava/guava/27.0-jre/guava-27.0-jre.jar

# Kafka
KAFKA_BIN_URI = https://archive.apache.org/dist/kafka/${KAFKA_VERSION}/kafka_${KAFKA_SCALA_VERSION}-${KAFKA_VERSION}.tgz
# KAFKA_BIN_URI = https://downloads.apache.org/kafka/${KAFKA_VERSION}/kafka_${KAFKA_SCALA_VERSION}-${KAFKA_VERSION}.tgz

# Elastic
ELASTIC_FILEBEAT_URI = https://artifacts.elastic.co/downloads/beats/metricbeat/metricbeat-${ES_VERSION}-amd64.deb
ELASTIC_METRICBEAT_URI = https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-${ES_VERSION}-amd64.deb

# MINICONDA = https://repo.anaconda.com/miniconda/Miniconda3-py38_4.10.3-Linux-x86_64.sh


#############################
#          TARGETS          #
#############################


# wget (= curl -L -O )
# -nc, --no-clobber 기존 파일에 다운로드(덮어쓰기) 할 경우 다운로드 건너뛰기
# -N,  --timestamping 로컬 파일보다 최신이 아니면 파일을 다시 가져오지 않음
# -P: 지정한 디렉토리에 다운로드
# --no-check-certificate 서버 인증서 검증하지 않음

.PHONY: build-assets
build-assets:
	mkdir -p ./hadoop/core/assets
	wget ${HADOOP_BIN_URI} -nc -O ./hadoop/core/assets/hadoop-${HADOOP_VERSION}.tar.gz || exit 0

	mkdir -p ./hadoop/ecosystems/spark/assets
	mkdir -p ./hadoop/ecosystems/spark/assets/jars
	wget ${SPARK_BIN_URI} -nc -O ./hadoop/ecosystems/spark/assets/$(shell basename ${SPARK_BIN_URI}) || exit 0
	wget ${SPARK_DELTA_CORE_JAR_URI} -nc -O ./hadoop/ecosystems/spark/assets/jars/$(shell basename ${SPARK_DELTA_CORE_JAR_URI}) || exit 0
	wget ${SPARK_DELTA_STORAGE_JAR_URI} -nc -O ./hadoop/ecosystems/spark/assets/jars/$(shell basename ${SPARK_DELTA_STORAGE_JAR_URI}) || exit 0
	wget ${SPARK_MSSQL_JDBC_CONNECTOR_URI} -nc -O ./hadoop/ecosystems/spark/assets/jars/$(shell basename ${SPARK_MSSQL_JDBC_CONNECTOR_URI}) || exit 0
	wget ${SPARK_MSSQL_CONNECTOR_FOR_SPARK_3_4_URI} -nc -O ./hadoop/ecosystems/spark/assets/jars/$(shell basename ${SPARK_MSSQL_CONNECTOR_FOR_SPARK_3_4}) || exit 0
	wget ${SPARK_ES_CONNECTOR_JAR_URI} -nc -O ./hadoop/ecosystems/spark/assets/jars/$(shell basename ${SPARK_ES_CONNECTOR_JAR_URI}) || exit 0

	mkdir -p ./hadoop/ecosystems/hive/assets
	mkdir -p ./hadoop/ecosystems/hive/assets/lib
	wget ${HIVE_BIN_URI} -nc -O ./hadoop/ecosystems/hive/assets/$(shell basename ${HIVE_BIN_URI}) || exit 0
	wget ${HIVE_MYSQL_CONNECTOR_URI} -nc -O ./hadoop/ecosystems/hive/assets/lib/$(shell basename ${HIVE_MYSQL_CONNECTOR_URI}) || exit 0
	wget ${HIVE_GUAVA_JAR_URI} -nc -O ./hadoop/ecosystems/hive/assets/lib/$(shell basename ${HIVE_GUAVA_JAR_URI}) || exit 0

	mkdir -p ./kafka/assets
	wget ${KAFKA_BIN_URI} -nc -O ./kafka/assets/$(shell basename ${KAFKA_BIN_URI}) || exit 0

	mkdir -p ./elastic/elasticsearch/assets
	wget ${ELASTIC_FILEBEAT_URI} -nc -O ./elastic/elasticsearch/assets/$(shell basename ${ELASTIC_FILEBEAT_URI}) || exit 0
	wget ${ELASTIC_METRICBEAT_URI} -nc -O ./elastic/elasticsearch/assets/$(shell basename ${ELASTIC_METRICBEAT_URI}) || exit 0

	# wget ${FILEBEAT_BIN_URI} -NP ./server/assets

# ifeq ($(shell ls ./hadoop/assets/hadoop-${HADOOP_VERSION}.tar.gz &> /dev/null || echo 0 && echo 1), 0)
# 	wget ${HADOOP_BIN_URI} -NP ./hadoop/assets
# endif
# ifeq ($(shell ls ./hadoop/assets/hadoop-${HADOOP_VERSION}-aarch64.tar.gz &> /dev/null || echo 0 && echo 1), 1)
# 	mv ./hadoop/assets/hadoop-${HADOOP_VERSION}-aarch64.tar.gz ./hadoop/assets/hadoop-${HADOOP_VERSION}.tar.gz
# endif

.PHONY: build-os
build-os:
	docker image build ./os -t ${PROJECT_NAME}:os

.PHONY: up
up:
	docker compose up -d --build

.PHONY: down
down:
	docker compose down

.PHONY: restart
restart: down up

.PHONY: log
log:
	docker compose logs -tf
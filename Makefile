SHELL = /bin/zsh
ARCH = $(shell arch)
PROJECT_NAME = data-infra

# BINARIES
HADOOP_VERSION = 3.3.6
ifneq (${ARCH}, $(filter ${ARCH}, arm64 aarch64))
	HADOOP_BIN_URI = https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz
else
	HADOOP_BIN_URI = https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}-aarch64.tar.gz
endif

SPARK_VERSION = 3.4.2
SPARK_BIN_URI = https://dlcdn.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz

HIVE_VERSION = 3.1.3
HIVE_BIN_URI = https://dlcdn.apache.org/hive/hive-${HIVE_VERSION}/apache-hive-${HIVE_VERSION}-bin.tar.gz

KAFKA_BIN_URI = https://dlcdn.apache.org/kafka/2.6.3/kafka_2.13-2.6.3.tgz
FILEBEAT_BIN_URI = https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.16.2-linux-x86_64.tar.gz
# MINICONDA = https://repo.anaconda.com/miniconda/Miniconda3-py38_4.10.3-Linux-x86_64.sh

# JARS
DELTA_CORE_JAR_URI = https://repo1.maven.org/maven2/io/delta/delta-core_2.12/2.4.0/delta-core_2.12-2.4.0.jar
DELTA_STORAGET_JAR_URI = https://repo1.maven.org/maven2/io/delta/delta-storage/2.4.0/delta-storage-2.4.0.jar
MYSQL_CONNECTOR_JAR_URI = https://repo1.maven.org/maven2/mysql/mysql-connector-java/5.1.46/mysql-connector-java-5.1.46.jar
GUAVA_JAR_URI = https://repo1.maven.org/maven2/com/google/guava/guava/27.0-jre/guava-27.0-jre.jar


################### TARGETS ###################

# wget (= curl -L -O )
# -nc, --no-clobber 기존 파일에 다운로드(덮어쓰기) 할 경우 다운로드 건너뛰기
# -N,  --timestamping 로컬 파일보다 최신이 아니면 파일을 다시 가져오지 않음
# -P: 지정한 디렉토리에 다운로드
# --no-check-certificate 서버 인증서 검증하지 않음

.PHONY: download-resources
download-resources:
	wget ${HADOOP_BIN_URI} -nc -O ./hadoop/resources/hadoop-${HADOOP_VERSION}.tar.gz || exit 0
	wget ${SPARK_BIN_URI} -nc -O ./hadoop/resources/spark-${SPARK_VERSION}-bin-hadoop3.tgz || exit 0
	wget ${HIVE_BIN_URI} -nc -O ./hadoop/resources/apache-hive-${HIVE_VERSION}-bin.tar.gz || exit 0
	wget ${DELTA_CORE_JAR_URI} -nc -O ./hadoop/resources/delta-core_2.12-2.4.0.jar || exit 0
	wget ${DELTA_STORAGET_JAR_URI} -nc -O ./hadoop/resources/delta-storage-2.4.0.jar || exit 0
	wget ${MYSQL_CONNECTOR_JAR_URI} -nc -O ./hadoop/resources/mysql-connector-java-5.1.46.jar || exit 0
	wget ${GUAVA_JAR_URI} -nc -O ./hadoop/resources/guava-27.0-jre.jar || exit 0

	# wget {${MYSQL_CONNECTOR_JAR_URI},${SPARK_BIN_URI}} -NP ./spark/resources
	# wget ${KAFKA_BIN_URI} -NP ./kafka/resources
	# wget ${FILEBEAT_BIN_URI} -NP ./server/resources

# ifeq ($(shell ls ./hadoop/resources/hadoop-${HADOOP_VERSION}.tar.gz &> /dev/null || echo 0 && echo 1), 0)
# 	wget ${HADOOP_BIN_URI} -NP ./hadoop/resources
# endif
# ifeq ($(shell ls ./hadoop/resources/hadoop-${HADOOP_VERSION}-aarch64.tar.gz &> /dev/null || echo 0 && echo 1), 1)
# 	mv ./hadoop/resources/hadoop-${HADOOP_VERSION}-aarch64.tar.gz ./hadoop/resources/hadoop-${HADOOP_VERSION}.tar.gz
# endif

.PHONY: build-os
build-os:
	docker image build ./os -t ${PROJECT_NAME}:os

.PHONY: up
up: build-os
	docker compose up -d --build

.PHONY: down
down:
	docker compose down

.PHONY: restart
restart: down up

.PHONY: log
log:
	docker compose logs -tf
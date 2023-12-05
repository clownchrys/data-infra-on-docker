SHELL = /bin/zsh

ARCH := (shell arch)
PROJECT_NAME := data-infra

# wget (= curl -L -O )
# -nc, --no-clobber 기존 파일에 다운로드(덮어쓰기) 할 경우 다운로드 건너뛰기
# -N,  --timestamping 로컬 파일보다 최신이 아니면 파일을 다시 가져오지 않음
# -P: 지정한 디렉토리에 다운로드
# --no-check-certificate 서버 인증서 검증하지 않음

MYSQL_CONNECTOR = https://repo1.maven.org/maven2/mysql/mysql-connector-java/5.1.46/mysql-connector-java-5.1.46.jar
GUAVA = https://repo1.maven.org/maven2/com/google/guava/guava/27.0-jre/guava-27.0-jre.jar
HADOOP = https://dlcdn.apache.org/hadoop/common/hadoop-3.3.1/hadoop-3.3.1.tar.gz
HIVE = https://dlcdn.apache.org/hive/hive-3.1.2/apache-hive-3.1.2-bin.tar.gz
PIG = https://dlcdn.apache.org/pig/pig-0.17.0/pig-0.17.0.tar.gz
# MINICONDA = https://repo.anaconda.com/miniconda/Miniconda3-py38_4.10.3-Linux-x86_64.sh
SPARK = https://dlcdn.apache.org/spark/spark-3.1.2/spark-3.1.2-bin-hadoop3.2.tgz
KAFKA = https://dlcdn.apache.org/kafka/2.6.3/kafka_2.13-2.6.3.tgz
FILEBEAT = https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.16.2-linux-x86_64.tar.gz

.PHONY: download-resources
download-resources:
	wget ${HADOOP} -NP ./hadoop/resources
	# wget {$MYSQL_CONNECTOR,$GUAVA,$HIVE} -NP ./hive/resources
	# wget $PIG -NP ./pig/resources
	# wget {$MYSQL_CONNECTOR,$SPARK} -NP ./spark/resources
	# wget $KAFKA -NP ./kafka/resources
	# wget $FILEBEAT -NP ./server/resources

.PHONY: build-os
build-os:
	docker image build ./os -t ${PROJECT_NAME}:os

.PHONY: up
up: download-resources build-os
	docker compose up -d --build

.PHONY: down
down:
	docker compose down

.PHONY: restart
restart: down up
CREATE DATABASE IF NOT EXISTS metastore;
CREATE USER 'hive-user'@'%' IDENTIFIED BY 'hive-user';
GRANT ALL PRIVILEGES ON metastore.* TO 'hive-user'@'%';
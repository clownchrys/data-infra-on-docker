#!/bin/sh

USERNAME=airflow
PASSWORD=airflow
EMAIL=airflow@airflow.org
FIRSTNAME=Airflow
LASTNAME=Admin
ROLE=Admin  # Role: Admin, User, Op, Viewer, and Public

airflow db init && \
airflow users create --username ${USERNAME} --password ${PASSWORD} --email ${EMAIL} --firstname ${FIRSTNAME} --lastname ${LASTNAME} --role ${ROLE} && \
airflow standalone
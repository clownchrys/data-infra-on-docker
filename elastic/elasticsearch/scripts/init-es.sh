#!/bin/bash

service metricbeat start && \
service filebeat start && \
/usr/local/bin/docker-entrypoint.sh eswrapper
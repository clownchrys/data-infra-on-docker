#!/bin/bash

elasticsearch-certutil ca --days 730
elasticsearch-certutil cert --days 730 \
--ca elastic-stack-ca.p12 \
--in config/instances.yml \
--out certs.zip \
--silent
unzip -d certs certs.zip
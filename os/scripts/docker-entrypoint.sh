#!/bin/bash

# sudo service ssh start
echo "[docker-entrypoint.sh] Starting OpenBSD Secure Shell server" && sudo /usr/sbin/sshd && \
echo "[docker-entrypoint.sh] Command Execution: '$*'" && eval "$*"
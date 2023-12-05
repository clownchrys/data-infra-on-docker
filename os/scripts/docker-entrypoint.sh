#!/bin/bash

# sudo service ssh start
echo "Starting OpenBSD Secure Shell server" && sudo /usr/sbin/sshd && \
echo "Command Execution:" && eval "$*"
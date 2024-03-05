#!/bin/bash

echo 'start FastAPI Server(gunicorn) in background'

# su -u ec2-user -c \
# 'echo account: `whoami`; \
# set -e; \
# source /home/ec2-user/api/venv/bin/activate; \
# cd /home/ec2-user/api; \
# pwd; \
# /home/ec2-user/api/venv/bin/gunicorn main:app \
# -k uvicorn.workers.UvicornWorker \
# --logger-class common.logger.SubbedGunicornLogger \
# --access-logfile /var/log/apirepository/access.log \
# --error-logfile /var/log/apirepository/error.log \
# --bind 0.0.0.0:8000 \
# --workers 1 \
# --threads 1 \
# --daemon \
# --preload'

gunicorn main:app -c config/gunicorn.py
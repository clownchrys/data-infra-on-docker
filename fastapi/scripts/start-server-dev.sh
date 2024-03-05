#!/bin/bash

echo 'start FastAPI Server(gunicorn) in background'

uvicorn main:app \
--host 0.0.0.0 \
--port 8000 \
--access-log \
--use-colors \
--proxy-headers \
--server-header \
--date-header \
--workers 2 \
--reload

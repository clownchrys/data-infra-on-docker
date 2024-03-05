#!/bin/bash

PID=`/usr/bin/pgrep -f main:app`

if [[ -n `$PID` ]]
then
  /usr/bin/kill -9 $PID
  echo 'FastAPI Server Stop normally'
else
  echo 'No such process. Please Start new FastAPI server'
fi

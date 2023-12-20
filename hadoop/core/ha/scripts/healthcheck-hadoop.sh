#!/bin/bash

CHECK_NN=true
CHECK_RM=true

NN_IDS=(nn1 nn2)
RM_IDS=(rm1 rm2)
EXIT_CODES=()

if [ "$CHECK_NN" = "true" ]; then
    for id in ${NN_IDS[*]}; do
        hdfs haadmin -checkHealth $id >> /dev/null 2>&1
        EXIT_CODES[${#EXIT_CODES[*]}]=$?
    done
fi

if [ "$CHECK_RM" = "true" ]; then
    for id in ${RM_IDS[*]}; do
        yarn rmadmin -checkHealth $id >> /dev/null 2>&1
        EXIT_CODES[${#EXIT_CODES[*]}]=$?
    done
fi

max_exit_code=$(printf "%s\n" ${EXIT_CODES[*]} | sort -gr | head -n1)

if [ "$max_exit_code" = "0" ]; then
    echo 'healthy'
else
    echo 'unhealthy'
    exit 1
fi
#!/bin/bash

FILE_NAME=$0

usage() {
    echo "Usage: will be printed"
}

# optional checking
if [[ $# -lt 1 ]]; then
    echo "$FILE_NAME: requires some options"
    usage
    exit 1
fi

# set opts
opts=$(getopt \
        --longoptions nn,rm \
        --name $FILE_NAME \
        -- "$@"
)

# validate opts
if [ $? -ne 0 ]; then
    usage
    exit 1
fi

# processing opts
set -- $opts

EXIT_CODES=()

NN_IDS=(nn1 nn2)
RM_IDS=(rm1 rm2)

while true; do
    case $1 in
        --nn)
            for id in ${NN_IDS[*]}; do
                hdfs haadmin -checkHealth $id >> /dev/null 2>&1
                EXIT_CODES[${#EXIT_CODES[*]}]=$?
            done
            shift 1
            ;;
        --rm)
            for id in ${RM_IDS[*]}; do
                yarn rmadmin -checkHealth $id >> /dev/null 2>&1
                EXIT_CODES[${#EXIT_CODES[*]}]=$?
            done
            shift 1
            ;;
        --)
            break
            ;;
        *)
            echo "$FILE_NAME: option recognized, but not implemented: $1"
            usage
            exit 1
            ;;
    esac
done

max_exit_code=$(printf "%s\n" ${EXIT_CODES[*]} | sort -gr | head -n1)

if [ "$max_exit_code" = "0" ]; then
    echo 'healthy'
else
    echo 'unhealthy'
    exit 1
fi

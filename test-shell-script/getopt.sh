#!/bin/bash

FILE_NAME=$0

usage() {
        echo "[SYSTEM] Usage will be printed"
}

# set opts
opts=$(getopt \
        --options ab:c: \
        --longoptions along,blong:,clong: \
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

while true; do
        case $1 in
                -a | --along)
                        echo "$1 detected"
                        shift 1
                        ;;
                -b | --blong)
                        echo "$1 detected: $2"
                        shift 2
                        ;;
                -c | --clong)
                        echo "$1 detected: $2"
                        shift 2
                        ;;
                --)
                        echo "-- $2 (entrypoint will be processed...)"
                        break
                        ;;
                *)
                        echo "$FILE_NAME: option recognized, but not implemented: $1"
                        usage
                        exit 1
                        ;;
        esac

done
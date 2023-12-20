#!/bin/bash

###################################
#         With Opt Value          #
###################################

OPTS_WITH_VAL=(
    "opt-one"
    "opt-two"
    "opt-three"
)

OPTS_WITH_VAL_DESC=(
    "description of opt-one"
    "description of opt-two"
    "description of opt-three"
)

######################################
#         Without Opt Value          #
######################################

OPTS_WITHOUT_VAL=(
    "opt-only1"
    "opt-only2"
    "opt-only3"
    "help"
)

OPTS_WITHOUT_VAL_DESC=(
    "description of opt-only1"
    "description of opt-only2"
    "description opt-only3"
    "print usage"
)

##########################
#         Usage          #
##########################

function print_usage() {
    pg_name=`basename $0`
    _opts_list_with_val=$(printf "[--%s=<val>] " "${OPTS_WITH_VAL[@]}")
    _opts_list_no_val=$(printf "[--%s] " "${OPTS_WITHOUT_VAL[@]}")

    echo ""
    echo "USAGE:"
    echo "  $pg_name ${_opts_list_with_val}"
    echo "        ${_opts_list_no_val}"

    echo ""
    echo "DESCRIPTIONS:"

    # 값을 필요로 하는 옵션들의 설명 출력
    for (( i=0 ; i<${#OPTS_WITH_VAL[@]} ; i++)) ;
    do
        printf "    --%s=<val>,\t%s\n" ${OPTS_WITH_VAL[$i]} "${OPTS_WITH_VAL_DESC[$i]}"
    done

    # 값이 필요없는 옵션 설명 출력
    for (( i=0 ; i<${#OPTS_WITHOUT_VAL[@]} ; i++)) ;
    do
        printf "    --%s,\t%s\n" ${OPTS_WITHOUT_VAL[$i]} "${OPTS_WITHOUT_VAL_DESC[$i]}"
    done
}

#########################################
#         Opt Count Validation          #
#########################################

if [[ $# -lt 1 ]]; then
    echo "ERROR: need args"
    print_usage
    exit
fi

#####################################
#         Opt Format & Set          #
#####################################

_opts_list_with_val=$(printf "%s:," "${OPTS_WITH_VAL[@]}")
_opts_list_no_val=$(printf "%s," "${OPTS_WITHOUT_VAL[@]}")
opts_list_str=${_opts_list_with_val}${_opts_list_no_val}

# read arguments
opts=$(getopt \
    --longoptions $opts_list_str \
    --name "$(basename "$0")" \
    --options "h?" \
    -- "$@"
)

if [[ $? -ne 0 ]]; then
  print_usage
  exit 1
fi

eval set --$opts

###################################
#         Opt Processing          #
###################################

while [[ $# -gt 0 ]]; do
    value=""

    case "$1" in
        "--"${OPTS_WITH_VAL[0]})
            value=$2
            shift 2
            ;;

        "--"${OPTS_WITH_VAL[1]})
            value=$2
            shift 2
            ;;

        "--"${OPTS_WITH_VAL[2]})
            value=$2
            shift 2
            ;;

        "--"${OPTS_WITHOUT_VAL[0]})
            echo ${1#--} is on
            shift 1
            ;;

        "--"${OPTS_WITHOUT_VAL[1]})
            echo ${1#--} is on
            shift 1
            ;;

        "--"${OPTS_WITHOUT_VAL[2]})
            echo ${1#--} is on
            shift 1
            ;;

        "h"|"?"|"--"${OPTS_WITHOUT_VAL[3]})  # --help
            print_usage
            exit 0
            ;;

        "--")
            echo "-- End of options --"
            break
            ;;
        
        *)
            print_usage
            exit 1
            ;;
    esac

    if [[ ! -z $value ]]; then
        echo $value;
    fi

done

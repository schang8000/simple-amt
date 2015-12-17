#!/bin/bash

if [ $# -lt 2 ]; then
    echo "usage: $0 <template_name> <experiment_id> [--prod]"
    exit 1
fi


TEMPLATE="${1}.html"

if [ $3 = "--prod" ]; then
  ID_FILE="${1}/hit_ids_pilot_${2}.txt"
  OUTPUT="${1}/pilot_${2}_result.txt"
else
  ID_FILE="${1}/hit_ids_pilot_${2}_sandbox.txt"
  OUTPUT="${1}/pilot_${2}_result_sandbox.txt"
fi

echo "*****  Launching HITs with the following parameters:"
echo $ID_FILE
echo $OUTPUT

python get_results.py \
  --hit_ids_file $ID_FILE \
  > $OUTPUT $3

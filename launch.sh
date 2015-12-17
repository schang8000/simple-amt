#!/bin/bash

if [ $# -lt 2 ]; then
    echo "usage: $0 <template_name> <experiment_id> [--prod]"
    exit 1
fi


TEMPLATE="${1}.html"

if [[ $3 = "--prod" ]]; then
  PROPERTY="hit_properties/${1}.json"
  INPUT="${1}/pilot_${2}_input.txt"
  HIT_ID="${1}/hit_ids_pilot_${2}.txt"
else
  PROPERTY="hit_properties/${1}_sandbox.json"
  INPUT="${1}/pilot_${2}_input.txt"
  HIT_ID="${1}/hit_ids_pilot_${2}_sandbox.txt"
fi

echo "#####Launching HITs with the following parameters:"
echo $PROPERTY
echo $INPUT
echo $HIT_ID

python launch_hits.py   --html_template="${TEMPLATE}" \
    --hit_properties_file="${PROPERTY}" \
    --input_json_file="${INPUT}" \
    --hit_ids_file="${HIT_ID}" $3

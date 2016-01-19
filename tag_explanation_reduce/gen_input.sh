#!/bin/bash

if [ $# -lt 1 ]; then
    echo "usage: $0 <experiment_id>"
    exit 1
fi

INPUT="../tag_explanation/expt_${1}_result.txt"
OUTPUT="./expt_${1}_input.txt"

python generate_turk_input.py --input "${INPUT}" \
  --output "${OUTPUT}" \

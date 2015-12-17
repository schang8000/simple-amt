#!/bin/bash

if [ $# -lt 1 ]; then
    echo "usage: $0 <experiment_id>"
    exit 1
fi

INPUT="/Users/shuochang/Google Drive/2015-Q4-crowd-explanation/mturk/simple-amt/tag_explanation/pilot_${1}_result.txt"
OUTPUT="/Users/shuochang/Google Drive/2015-Q4-crowd-explanation/mturk/simple-amt/tag_explanation_reduce/pilot_${1}_input.txt"

python tag_explanation_reduce/generate_turk_input.py --input "${INPUT}" \
  --output "${OUTPUT}" \

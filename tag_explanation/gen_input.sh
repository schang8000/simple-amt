#!/bin/bash

if [ $# -lt 1 ]; then
    echo "usage: $0 <experiment_id>"
    exit 1
fi

TAG_GROUP_INPUT="../tag_group/expt_${1}_input.txt"
TAG_GROUP_OUTPUT="../tag_group/expt_${1}_result.txt"
OUTPUT="./expt_${1}_input.txt"
SEARCH_INDEX_DIR="./review_indexes"

python generate_turk_input.py --tag_group_input "${TAG_GROUP_INPUT}" \
--tag_group_output "${TAG_GROUP_OUTPUT}" \
  --output "${OUTPUT}" \
  --search_index "${SEARCH_INDEX_DIR}"

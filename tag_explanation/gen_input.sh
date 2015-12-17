#!/bin/bash

if [ $# -lt 1 ]; then
    echo "usage: $0 <experiment_id>"
    exit 1
fi

TAG_GROUP_INPUT="/Users/user/Google Drive/2015-Q4-crowd-explanation/mturk/simple-amt/tag_group/pilot_${1}_input.txt"
TAG_GROUP_OUTPUT="/Users/user/Google Drive/2015-Q4-crowd-explanation/mturk/simple-amt/tag_group/pilot_${1}_result.txt"
OUTPUT="/Users/user/Google Drive/2015-Q4-crowd-explanation/mturk/simple-amt/tag_explanation/pilot_${1}_input.txt"
SEARCH_INDEX_DIR="/Users/user/Google Drive/2015-Q4-crowd-explanation/mturk/simple-amt/tag_explanation/review_indexes"

python tag_explanation/generate_turk_input.py --tag_group_input "${TAG_GROUP_INPUT}" \
--tag_group_output "${TAG_GROUP_OUTPUT}" \
  --output "${OUTPUT}" \
  --search_index "${SEARCH_INDEX_DIR}"

#!/bin/bash

MODEL_PATH="/Users/user/Documents/workspace/semantic/word2vec_data/imdb_model_1000"
GENOME_FILE="/Users/user/Documents/workspace/semantic/data/movie_genome.csv"
MOVIE_DETAIL_FILE="/Users/user/Documents/workspace/semantic/data/movie_details.csv"
NUM="10"
MOVIE_ID_OUT="./sample_movies.txt"
OUT="./turk_input_movies.txt"

python generate_movie_tag_clusters.py --model_path $MODEL_PATH \
  --movie_genome_path $GENOME_FILE \
  --movie_detail_path $MOVIE_DETAIL_FILE \
  --num_movie $NUM \
  --movie_id_file_output $MOVIE_ID_OUT \
  --output $OUT

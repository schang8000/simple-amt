#!/bin/bash

MODEL_PATH="/Users/user/Documents/workspace/semantic/word2vec_data/imdb_model_1000"
GENOME_FILE="/Users/user/Documents/workspace/semantic/data/movie_genome.csv"
MOVIE_DETAIL_FILE="/Users/user/Documents/workspace/semantic/data/movie_details.csv"
NUM="200"
MOVIE_ID_OUT="./full_expt_movies.txt"
OUT="./full_expt_input.txt"

ssh -f schang@movielens.cs.umn.edu -L 3306:movielens.cs.umn.edu:3306 -N
python generate_movie_tag_clusters.py --model_path $MODEL_PATH \
  --movie_genome_path $GENOME_FILE \
  --movie_detail_path $MOVIE_DETAIL_FILE \
  --num_movie $NUM \
  --movie_id_file_output $MOVIE_ID_OUT \
  --output $OUT

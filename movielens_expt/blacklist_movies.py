import sys
import pymysql
import gensim
import argparse
import pandas as pd

DB_HOST = 'localhost'
DB_USER = 'web'
DB = 'ML3_mirror'
WORD2VEC_MODEL = "/Users/user/Documents/workspace/semantic/word2vec_data/imdb_model_1000"
TAG = "/Users/user/Documents/workspace/semantic/data/movie_genome.csv"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pwd', required=True, help="Password to database")
    args = parser.parse_args()
    model = gensim.models.Doc2Vec.load(WORD2VEC_MODEL)
    genome = pd.read_csv(TAG)
    tags = pd.unique(genome['tag'])
    tags_no_space = [x.replace(' ', '_') for x in tags]
    imdb_tags = filter(lambda x: x not in model.vocab, tags_no_space)
    tags_space = [x.replace('_', ' ') for x in imdb_tags]
    con = pymysql.connect(host=DB_HOST, db=DB, user=DB_USER, password=args.pwd)
    pd.DataFrame({'tag': tags_space}).to_sql(
        'expt_crowd_expl_tag_blacklist', con, flavor='mysql', if_exists='append', index=False)

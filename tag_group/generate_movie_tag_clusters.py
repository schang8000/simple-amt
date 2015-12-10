import pandas as pd
import json
import sklearn
from sklearn.cluster import AffinityPropagation
from sklearn.metrics import pairwise
import argparse
import sys
import pymysql
import gensim

class Word2VecClusterer(object):
    """A clusterer that uses word2vec models.
    """
    def __init__(self, model_path):
        """Initialze clusterer by loading a word2vec model.
        """
        self.model = gensim.models.Doc2Vec.load(model_path)

    def filter_genome(self, genome):
        """Filter out tags in movie genome that are not in the word2vec model.

        Args:
            genome: A DataFrame storing movie genome with tags stored in the column 'tag'.

        Returns:
            Filtered movie genome DataFrame.
        """
        tags = pd.unique(genome['tag'])
        tags_no_space = [x.replace(' ', '_') for x in tags]
        imdb_tags = filter(lambda x: x in self.model.vocab, tags_no_space)
        movie_genome_imdb = genome[genome.tag.isin(imdb_tags)]
        return movie_genome_imdb

    def cluster(self, cluster_model, tags=[], distance=False):
        """Cluster tags using tag similarity matrix.

        Args:
            tags: A list of tags to cluster.

        Returns:
            Clustering result stored in a dict.
        """
        vectors = []
        for t in tags:
            vectors.append(self.model[t])
        if distance:
            labels = cluster_model.fit_predict(vectors)
        else:
            sim_mat = 1 - pairwise.pairwise_distances(vectors, metric='cosine')
            labels = cluster_model.fit_predict(sim_mat)
        result = {}
        for l, t in zip(labels, tags):
            if l not in result:
                result[l] = [t]
            else:
                result[l].append(t)
        formated_result = []
        for _, tags in result.iteritems():
            cluster = {}
            cluster['tags'] = []
            for t in tags:
                cluster['tags'].append({'name': t})
            formated_result.append(cluster)
        return formated_result

def top_n(x, col, n):
    return x.sort_values(by=[col], ascending=False)[0:n]

if __name__ == "__main__":
    NUM_TAGS = 20
    TMDB_IMG_URL = 'http://image.tmdb.org/t/p/original'
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_path', required=True, help="Path to a word2vec model")
    parser.add_argument('--movie_genome_path', required=True, help="Path to a movie genome file")
    parser.add_argument('--movie_detail_path', required=True, help="Path to a movie detail file")
    parser.add_argument('--num_movie', type=int, help="Number of movies to sample")
    parser.add_argument('--output', help="Path to write out json result")
    parser.add_argument('--movie_id_file', help="A text file with one movie id in each line")
    parser.add_argument('--movie_id_file_output', help="Path to write out movie ids")
    args = parser.parse_args()
    # Read in files
    movie_genome = pd.read_csv(args.movie_genome_path, index_col=0, low_memory=False)
    movie_detail = pd.read_csv(args.movie_detail_path, index_col=0, low_memory=False)
    movie_detail_genome = movie_detail[
        movie_detail.movieId.isin(set(movie_genome.movie_id))
        ].sort_values(by=['rating_density'], ascending=False)
    movie_ids = []
    if args.movie_id_file:
        with open(args.movie_id_file) as f:
            for line in f.readlines():
                movie_ids.append(line.strip())
    else:
        movie_ids += list(movie_detail_genome[:500].sample(n=args.num_movie/2).movieId)
        movie_ids += list(movie_detail_genome[500:1000].sample(
            n=args.num_movie - args.num_movie/2).movieId)
        with open(args.movie_id_file_output, 'w') as f:
            for mid in movie_ids:
                f.write(str(mid) + '\n')
    # Get tmdb data from database.
    try:
        con = pymysql.connect(host="movielens.cs.umn.edu", db="ML3", user="readonly")
        tmdb_data = pd.read_sql("select * from movie_tmdb_data where movieId in (%s)" % str(movie_ids).strip('[]'), con)
    except:
        sys.exit("Error connecting to tmdb db!")
    clusterer = Word2VecClusterer(args.model_path)
    ap = AffinityPropagation(damping=0.5, affinity="precomputed")
    movie_genome_imdb = clusterer.filter_genome(movie_genome)
    top_20_tags_imdb = movie_genome_imdb.groupby('movie_id').apply(lambda x: top_n(x, 'relevance', 20)).reset_index(drop=1)
    print "Writing movies..."
    with open(args.output or "turk_movies.json", 'w') as f:
        for mid in movie_ids:
            movie = {'movieId': mid}
            movie['movieTitle'] = tmdb_data[tmdb_data.movieId==mid].title.values[0]
            movie['movieDescription'] = tmdb_data[tmdb_data.movieId==mid].plotSummary.values[0]
            movie['posterSrc'] = TMDB_IMG_URL + tmdb_data[tmdb_data.movieId==mid].posterPath.values[0]
            movie['clusters'] = clusterer.cluster(
                ap, tags=top_20_tags_imdb[top_20_tags_imdb.movie_id==mid].tag, distance=False)
            f.write(json.dumps(movie) + '\n')

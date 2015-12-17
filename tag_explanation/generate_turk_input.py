from index_review import ReviewSearchEngine
import pandas as pd
import numpy as np
import json
import argparse

NUM_QUOTES = 6

class FromTagspToExplanation(object):
    """Generate input to tag explanation HIT from results from tag group HITS.
    """
    def __init__(self, movie_info_file, infile, outfile, search_index_dir):
        self.movie_info_file = movie_info_file
        self.infile = infile
        self.outfile = outfile
        self.search_index_dir = search_index_dir

    def _transform_data(self, data):
        result = []
        mid = data['output']['movieId']
        for idx, cluster in enumerate(data['output']['clusters']):
            for tag in cluster['tags']:
                row = {}
                row['movieId'] = mid
                row['cluster'] = idx
                row['assignment_id'] = data['assignment_id']
                row['worker_id'] = data['worker_id']
                row['hit_id'] = data['hit_id']
                row['tag'] = tag['name']
                row['not_fit'] = 0 if not tag.get('Does not fit') else 1
                row['inappropriate'] = 0 if not tag.get('Inappropriate') else 1
                row['best'] = 1 if cluster.get('Best tag') == tag['name'] else 0
                result.append(row)
        return result

    def _pick_best_tag(self, x):
        x['cluster_label'] = x.ix[np.argmax(x['best']['mean'])]['tag'].values[0]
        return x

    def process(self):
        trans_output = []
        searcher = ReviewSearchEngine(self.search_index_dir)
        with open(self.infile, 'r') as f:
            for line in f.readlines():
                turk_output = dict(json.loads(line))
                trans_output += self._transform_data(turk_output)
        movie_info = {}
        with open(self.movie_info_file, 'r') as f:
            for line in f.readlines():
                movie = dict(json.loads(line))
                movie_info[movie['movieId']] = movie
        result = pd.DataFrame(trans_output)
        result_agg = result.groupby(
                        ['movieId', 'cluster', 'tag'])[['best', 'not_fit', 'inappropriate']
                        ].agg([np.mean, np.sum])
        result_agg = result_agg[(result_agg['not_fit']['mean']<0.5) &
                                (result_agg['inappropriate']['mean']<=0.5)
                                ].reset_index()
        result_agg = result_agg.groupby(
                        ['movieId', 'cluster']).apply(self._pick_best_tag)
        output_df = result_agg.groupby(
                    ['movieId', 'cluster_label'])['tag'].agg(
                        lambda x: tuple(x)).reset_index()
        output_df = output_df.groupby('movieId').apply(
                lambda x: x.to_dict(orient='records')).reset_index()
        with open(self.outfile, 'w') as f:
            for movie in output_df.iterrows():
                mid = movie[1]['movieId']
                clusters = movie[1][0]
                for cluster in clusters:
                    quotes = searcher.search(mid, cluster['cluster_label'])
                    quotes = quotes[:NUM_QUOTES]
                    if len(quotes) < NUM_QUOTES:
                        stop = False
                        for tag in cluster['tag']:
                            for quote in searcher.search(mid, tag):
                                if quote not in quotes:
                                    quotes.append(quote)
                                if len(quotes) >= NUM_QUOTES:
                                    stop = True
                                    break
                            if stop:
                                break
                    cluster['quotes'] = [quote['sentence'] for quote in quotes]

                movie_obj = {
                    'movieId': mid, 'clusters': clusters,
                    'movieTitle': movie_info.get(mid).get('movieTitle'),
                    'movieDescription': movie_info.get(mid).get('movieDescription'),
                    'posterSrc': movie_info.get(mid).get('posterSrc')
                    }
                f.write(
                    json.dumps(movie_obj) + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--tag_group_input', required=True, help="Path to input file to tag group HITs")
    parser.add_argument('--tag_group_output', required=True, help="Path to output from tag group HITs")
    parser.add_argument('--output', required=True, help="Path to output file")
    parser.add_argument('--search_index', required=True, help="Path to search index folder")
    args = parser.parse_args()
    processor = FromTagspToExplanation(
        args.tag_group_input, args.tag_group_output, args.output, args.search_index)
    processor.process()

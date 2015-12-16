from index_review import ReviewSearchEngine
import pandas as pd
import json

NUM_QUOTES = 6

class FromTagspToExplanation(object):
    """Generate input to tag explanation HIT from results from tag group HITS.
    """
    def __init__(self, infile, outfile, search_index_dir):
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
        with open(self.infile) as f:
            for line in f.readlines():
                turk_output = dict(json.loads(line))
                trans_output += self.transform_data(turk_output)
        result = pd.DataFrame(trans_output)
        result_agg = result.groupby(
                        ['movieId', 'cluster', 'tag'])[['best', 'not_fit', 'inappropriate']
                        ].agg([np.mean, np.sum])
        result_agg = result_agg[(result_agg['not_fit']['mean']<0.5) &
                                (result_agg['inappropriate']['mean']<=0.5)
                                ].reset_index()
        result_agg = result_agg.groupby(
                        ['movieId', 'cluster']).apply(self.pick_best_tag)
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
                    quotes = [quote for quote in
                        searcher.search(mid, cluster.cluster_label)]
                    quotes = quotes[:NUM_QUOTES]
                    if len(quotes) < NUM_QUOTES:
                        stop = False
                        for tag in cluster['tag']:
                            for quote in searcher.search(mid, tag):
                                quotes.append(quote)
                                if len(quotes) >= NUM_QUOTES:
                                    stop = True
                                    break
                            if stop:
                                break
                    cluster['quotes'] = quotes
                f.write(
                    json.dumps({'movieId': mid, 'clusters': clusters}) + '\n')

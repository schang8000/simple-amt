import pandas as pd
import numpy as np
import json
import argparse
import pymysql


DB_HOST = 'localhost'
DB_USER = 'web'
DB = 'ML3_mirror'


class ExportResult(object):

    def __init__(self, input_file, password):
        self.input = input_file
        self.password = password

    def _transform_data(self, data):
        result = []
        mid = data['output']['movieId']
        for idx, cluster in enumerate(data['output']['clusters']):
            row = {}
            row['movieId'] = int(mid)
            row['cluster'] = idx
            row['assignment_id'] = data.get('assignment_id')
            row['worker_id'] = data.get('worker_id')
            row['hit_id'] = data.get('hit_id')
            row['explanation'] = cluster.get('best_review')
            row['clusterLabel'] = cluster.get('cluster_label')
            row['clusterTags'] = ','.join(cluster.get('tag', []))
            result.append(row)
        return result

    def _pick_best_explanation(self, x):
        x = x.ix[np.argmax(x['count'])]
        return x

    def export(self):
        result_dicts = []
        with open(self.input, 'r') as f:
            for line in f.readlines():
                result_dicts += self._transform_data(dict(json.loads(line)))
        result_df = pd.DataFrame(result_dicts)
        result_df = (result_df.groupby(['movieId', 'cluster', 'clusterLabel', 'clusterTags', 'explanation'])
                            .size()
                            .reset_index()
                            .rename(columns={0:'count'}))
        output = result_df.groupby(
                ['movieId', 'clusterLabel', 'clusterTags']
            ).apply(self._pick_best_explanation).reset_index(drop=True).drop(['count', 'cluster'], 1)
        output['explanation'] = output['explanation'].apply(
            lambda x: x.replace("You like movies featuring ", "From your MovieLens profile it seems that you prefer movies tagged as "))
        output = output[~output['explanation'].isnull()]
        con = pymysql.connect(host=DB_HOST, db=DB, user=DB_USER, password=self.password)
        output.to_sql('expt_crowd_expl_explanations', con, flavor='mysql', if_exists='append', index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help="Path to result files of tag group reduce HITs")
    parser.add_argument('--pwd', required=True, help="Password to database")
    args = parser.parse_args()
    export_result = ExportResult(args.input, args.pwd)
    export_result.export()

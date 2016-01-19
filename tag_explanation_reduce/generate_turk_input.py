import json
import argparse

class PrepareTagExplanationReduceInput(object):
    def __init__(self, infile, outfile):
        self.infile = infile
        self.outfile = outfile

    def process(self):
        results = {}
        print self.infile
        with open(self.infile, 'r') as f:
            for line in f.readlines():
                res = json.loads(line)
                mid = res.get('output').get('movieId')
                if mid not in results:
                    results[mid] = [res.get('output')]
                else:
                    results[mid].append(res['output'])

        with open(self.outfile, 'w') as f:
            for mid, outputs in results.iteritems():
                movie = {}
                for output in outputs:
                    if not movie:
                        output.pop('comment')
                        movie = output
                        continue
                    for old, new in zip(
                        movie.get('clusters', []), output.get('clusters', [])):
                        if not 'review' in old:
                            continue
                        if not isinstance(old['review'], list):
                            old['review'] = [old['review']]
                            # Add num_adj as a list for verifiable questions.
                            old['num_adj'] = []
                        old['review'].append(new['review'])
                f.write(json.dumps(movie) + '\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help="Path to results from tag explanation HITs")
    parser.add_argument('--output', required=True, help="Path to output file")
    args = parser.parse_args()
    processor = PrepareTagExplanationReduceInput(
        args.input, args.output)
    processor.process()

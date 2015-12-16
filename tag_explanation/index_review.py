from whoosh.qparser import QueryParser
from whoosh.index import create_in
from whoosh.lang.morph_en import variations
from whoosh.filedb.filestore import FileStorage
from whoosh import index, sorting, query
from whoosh.fields import *
from pymysql import connect
from nltk.tokenize import sent_tokenize
from bs4 import BeautifulSoup
import os

HOST = 'localhost'
DB = 'movielens_imdb_data'

class ReviewSearchEngine(object):
    """Search engine for imdb reviews.

    Create index from Mysql database storing reviews and enables search for
    sentences with target word.
    """

    def __init__(self, indexDir):
        self.indexDir = indexDir
        schema = Schema(movieId=ID(stored=True), rating=NUMERIC(sortable=True, stored=True),
                        sentence=TEXT(stored=True), up_votes=NUMERIC(sortable=True, stored=True),
                        votes=NUMERIC(sortable=True, stored=True))
        if not os.path.exists(self.indexDir):
            os.mkdir(self.indexDir)
            print "Creating index folder at %s" % self.indexDir
            self.indexer = index.create_in(self.indexDir, schema=schema)
            return
        self.indexer = index.open_dir(self.indexDir)

    def create_index(self, user, pwd):
        con = connect(host=HOST, db=DB, user=user, password=pwd)
        index_writer = self.indexer.writer()
        with con.cursor() as cursor:
            cursor.execute(
                'SELECT movieId, rating, heading, review, up_votes, votes FROM imdb_review WHERE rating > 6')
            for result in cursor.fetchall():
                mid, rating, heading, review, up_votes, votes = result
                sentences = (sent_tokenize(BeautifulSoup(heading).get_text()) +
                            sent_tokenize(BeautifulSoup(review).get_text()))
                for sentence in sentences:
                    index_writer.add_document(
                        movieId=unicode(mid), rating=unicode(rating), sentence=unicode(sentence),
                        up_votes=unicode(up_votes or 0), votes=unicode(votes or 0))
            index_writer.commit()
        con.close()


    def search(self, mid, word):
        """Search reivew sentences with "word" on movie "mid".
        """
        with self.indexer.searcher() as searcher:
            qp = QueryParser("sentence", schema=self.indexer.schema,
                             termclass=query.Variations)
            q = qp.parse(unicode(word))
            allow_q = query.Term('movieId', unicode(mid))
            votes_sort = sorting.FieldFacet("votes", reverse=True)
            up_votes_sort = sorting.FieldFacet("up_votes", reverse=True)
            rating_sort = sorting.FieldFacet("rating", reverse=True)
            for res in searcher.search(q, filter=allow_q,
                                   sortedby=[up_votes_sort, rating_sort]):
                yield res

if __name__ == "__main__":
    search_engine = ReviewSearchEngine('review_indexes')
    pwd = raw_input('Password: ')
    search_engine.create_index('schang', pwd)
    mid = raw_input("movie:")
    word = raw_input("word:")
    while mid and word:
        for res in search_engine.search(mid, word):
            print res
        mid = raw_input("movie:")
        word = raw_input("word:")

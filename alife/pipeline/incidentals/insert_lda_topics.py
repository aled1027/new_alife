# Inserts a field for every document for their LDA topics (in decreasing order of strength)
from pymongo import MongoClient
from alife.txtmine.lda import load_lda
from pprint import pprint
from jmAlife.dbManage.parallelMap import parallelMap

def test(limit):
    # db = MongoClient().patents
    # lda = load_lda(lda_fn)
    # pnos = load_pno2id(pno2id_fn)
    # corpus = load_corpus(corpusfn)
    # doc_topics = [lda[doc] for doc in corpus]
    # def partfunc(doc):
    #    return {'$set': {'lda_topics': doc_topics[pno2id[doc['_id']]]}}
    # pats_test = db.traits.find().limit(limit)
    # for p in pats_test:
    #   pprint(partfunc(p))
    pass

def main():
    # db = MongoClient().patents
    # lda = load_lda(lda_fn)
    # pnos = load_pno2id(pno2id_fn)
    # corpus = load_corpus(corpusfn)
    # doc_topics = [lda[doc] for doc in corpus]
    # def partfunc(doc):
    #    return {'$set': {'lda_topics': doc_topics[pno2id[doc['_id']]]}}
    # parallelMap(
    #   partfunc,
    #   in_collection = db.traits,
    #   out_collection = db.traits,
    #   findArgs = {
    #     'spec': {},
    #     'fields': {},
    #   },
    #   updateFreq = 500,
    #   bSize = 1000
    #)
    pass

if __name__ == '__main__':
    test()


# Inserts a field for every document for their LDA topic indices and strengths (in decreasing order of strength)
from pymongo import MongoClient
from alife.txtmine.lda import load_lda, load_vocab, load_corpus
from alife.util.general import load_obj
from pprint import pprint
from jmAlife.dbManage.parallelMap import parallelMap

def test(limit):
    indir = '/Users/jmenick/Desktop/alife_refactor/output/lda_model_200'
    name = 'lda_200'
    ldafn = '/'.join([indir, name+'.lda'])
    corpusfn = '/'.join([indir, 'corpus_' + name + '.svmlight'])
    pnofn = '/'.join([indir, 'pnos.p'])
    corpus = load_corpus(corpusfn)
    pno2id = {pno:i for i,pno in enumerate(load_obj(pnofn))}
    lda = load_lda(ldafn)
    assert(len(pno2id) == len(corpus))
    def partfunc(doc):
        doc_topics = lda[corpus[pno2id[doc['_id']]]]
        return {'$set': {'lda_topics': doc_topics}}
    db = MongoClient().patents
    test_patns = db.pat_text.find().limit(limit)
    for patn in test_patns:
        pprint(partfunc(patn))

def main():
    indir = '/Users/jmenick/Desktop/alife_refactor/output/lda_model_200'
    name = 'lda_200'
    ldafn = '/'.join([indir, name+'.lda'])
    corpusfn = '/'.join([indir, 'corpus_' + name + '.svmlight'])
    pnofn = '/'.join([indir, 'pnos.p'])
    corpus = load_corpus(corpusfn)
    pno2id = {pno:i for i,pno in enumerate(load_obj(pnofn))}
    lda = load_lda(ldafn)
    assert(len(pno2id) == len(corpus))
    def partfunc(doc):
        doc_topics = lda[corpus[pno2id[doc['_id']]]]
        return {'$set': {'lda_topics': doc_topics}}
     db = MongoClient().patents
     parallelMap(
         partfunc,
         in_collection = db.traits,
         out_collection = db.traits,
         findArgs = {
             'spec': {},
             'fields': {},
         },
         updateFreq = 500,
         bSize = 1000
     )

if __name__ == '__main__':
    test()


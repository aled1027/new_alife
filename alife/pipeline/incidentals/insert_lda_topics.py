# Inserts a field for every document for their LDA topic indices and strengths (in decreasing order of strength)
from pymongo import MongoClient
from alife.txtmine.lda import load_lda, load_corpus, load_vocab
from alife.util.general import load_obj
from pprint import pprint
from jmAlife.dbManage.parallelMap import parallelMap
from pyLDAvis.gensim import prepare
import pyLDAvis

def test(limit=100):
    # Get filenames.
    indir = '/Users/jmenick/Desktop/alife_refactor/output/lda_model_200'
    name = 'lda_200'
    pnofn = '/'.join([indir, 'pnos.p'])
    ldafn = '/'.join([indir, name+'.lda'])
    corpusfn = '/'.join([indir, 'corpus'+name+'.svmlight'])
    vocabfn = '/'.join([indir, 'vocab.dict'])

    # Load persisted data from disk. 
    vocab = load_vocab(vocabfn)
    corpus = load_corpus(corpusfn)
    lda = load_lda(ldafn)
    pnos = load_obj(pnofn)
    pno2id = {p:i for i,p in enumerate(pnos)}

    #produce visualization. 
    visfn = '/'.join([indir, 'vis.html'])
    vis_data = prepare(lda, corpus, vocab)
    pyLDAvis.save_html(vis_data, visfn)

    # put doc topics in db. 
    assert(len(corpus) == len(pnos))
    db = MongoClient().patents
    def partfunc(doc):
        topics = lda[corpus[pno2id[doc['_id']]]]
        return {'$set': {'lda_topics': topics}}
    pats_test = db.traits.find().limit(limit)
    for p in pats_test:
        pprint(partfunc(p))

def main():
    # Get filenames. 
    indir = '/Users/jmenick/Desktop/alife_refactor/output/lda_model_200'
    name = 'lda_200'
    pnofn = '/'.join([indir, 'pnos.p'])
    ldafn = '/'.join([indir, name+'.lda'])
    corpusfn = '/'.join([indir, 'corpus'+name+'.svmlight'])
    vocabfn = '/'.join([indir, 'vocab.dict'])
    
    # Load persisted data from disk.
    vocab = load_vocab(vocabfn)
    corpus = load_corpus(corpusfn)
    lda = load_lda(ldafn)
    pnos = load_obj(pnofn)
    pno2id = {p:i for i,p in enumerate(pnos)}

    #produce visualization. 
    visfn = '/'.join([indir, 'vis.html'])
    vis_data = prepare(lda, corpus, vocab)
    pyLDAvis.save_html(vis_data, visfn)

    # put doc topics in db. 
    db = MongoClient().patents
    assert(len(corpus) == len(pnos))
    def partfunc(doc):
        pno = doc['_id']
        try: 
            corpus_idx = pno2id[pno]
            bow = corpus[corpus_idx]
            topics = lda[bow]
            return {'$set': {'lda_topics': topics}}
        except:
            # Is there some surt of null thing I can pass
            # to cursor.update() which does nothing?
            return None
    parallelMap(
        partfunc,
        in_collection = db.traits,
        out_collection = db.traits,
        findArgs = {
            # hmm. Want some way to spec that 
            'spec': {'top_tf-idf': {'$nin': [[]]}}, 
            'fields': {'_id':1}
        },
        bSize = 1000,
        updateFreq = 500
    )

if __name__ == '__main__':
    test()


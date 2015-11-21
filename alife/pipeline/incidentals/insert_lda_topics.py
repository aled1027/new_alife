# Inserts a field for every document for their LDA topic indices and strengths (in decreasing order of strength)
from pymongo import MongoClient
from alife.txtmine.lda import load_lda, load_corpus, load_vocab
from alife.util.general import load_obj
from pprint import pprint
from jmAlife.dbManage.parallelMap import parallelMap
from pyLDAvis.gensim import prepare
import pyLDAvis
import logging

def test(limit=100):
    # Get filenames.
    indir = '/Users/jmenick/Desktop/alife_refactor/output/lda_model_200'
    name = 'lda_200'
    pnofn = '/'.join([indir, 'pnos.p'])
    ldafn = '/'.join([indir, name+'.lda'])
    corpusfn = '/'.join([indir, 'corpus_'+name+'.svmlight'])
    vocabfn = '/'.join([indir, 'vocab_'+name+'.dict'])

    # Load persisted data from disk. 
    print "loading data..."
    vocab = load_vocab(vocabfn)
    corpus = load_corpus(corpusfn)
    lda = load_lda(ldafn)
    pnos = load_obj(pnofn)
    pno2id = {p:i for i,p in enumerate(pnos)}

    #produce visualization... commented out for now. keeps crashing the machine. 
#    print "producing visualization..."
#    visfn = '/'.join([indir, 'vis.html'])
#    vis_data = prepare(lda, corpus, vocab)
#    print "saving visualization..."
#    pyLDAvis.save_html(vis_data, visfn)

    # put doc topics in db. 
    print "Getting doc topics..."
    try:
        assert(len(corpus) == len(pnos))
    except:
        print "Corpus length: {}, pnos length: {}".format(len(corpus), len(pnos))
    db = MongoClient().patents
    def partfunc(doc):
        topics = lda[corpus[pno2id[doc['_id']]]]
        return {'$set': {'lda_topics': topics}}
    pats_test = list(db.traits.find().limit(limit)) + [db.traits.find_one({'_id': 4683202})]
    for p in pats_test:
        pprint("Pno: {} below".format(p['_id']))
        pprint(partfunc(p))
    print "\nDone."

def main():
    # Get filenames. 
    indir = '/Users/jmenick/Desktop/alife_refactor/output/lda_model_200'
    name = 'lda_200'
    pnofn = '/'.join([indir, 'pnos.p'])
    ldafn = '/'.join([indir, name+'.lda'])
    corpusfn = '/'.join([indir, 'corpus_'+name+'.svmlight'])
    vocabfn = '/'.join([indir, 'vocab_'+name+'.dict'])
        
    # Load persisted data from disk.
    print "loading data..."
    vocab = load_vocab(vocabfn)
    corpus = load_corpus(corpusfn)
    lda = load_lda(ldafn)
    pnos = load_obj(pnofn)
    pno2id = {p:i for i,p in enumerate(pnos)}

    #produce visualization... commented out for now due to crashing. Ugh PCA again...
#    visfn = '/'.join([indir, 'vis.html'])
#    vis_data = prepare(lda, corpus, vocab)
#    pyLDAvis.save_html(vis_data, visfn)

    # put doc topics in db. 
    print "inserting doc topics..."
    db = MongoClient().patents
    print "len(corpus): {}, len(pnos): {}".format(len(pnos), len(corpus))
    def partfunc(doc):
        pno = doc['_id']
        try: 
            corpus_idx = pno2id[pno]
            bow = corpus[corpus_idx]
            topics = lda[bow]
            return {'$set': {'lda_topics': topics}}
        except:
            logging.warning("no topics for {}".format(pno))
            return {'$set': {'no_topics': True}}
    parallelMap(
        partfunc,
        in_collection = db.traits,
        out_collection = db.traits,
        findArgs = {
            'spec': {},
            'fields': {'_id':1}
        },
        bSize = 1000,
        updateFreq = 500
    )

if __name__ == '__main__':
    test()
    #main()


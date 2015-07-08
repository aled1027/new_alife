# utilities for running LDA on our patent database. 
import sys
import csv
from gensim.models import ldamodel
from gensim import corpora
from pyLDAvis.gensim import prepare
from alife.util.dbutil import get_fields_unordered
from alife.mockdb import get_mock
from alife.txtmine.tokenizer import Tokenizer
import pyLDAvis

class MyLda:
    def __init__(self, n_topics, name=''):
        self.K = n_topics
        assert(type(name) == str)
        if name == '':
            self.name = 'lda_'+str(self.K)
        else:
            self.name = name
        self.tokenizer = Tokenizer()
        self.has_vocab = False
        self.has_corpus = False
        self.is_trained = False
        self.has_viz_data = False
        
    def load_vocab(self, fn):
        """loads a gensim vocab.dict object from disk."""
        vocab = corpora.Dictionary.load(fn)
        self.vocab = vocab
        self.has_vocab = True

    def load_corpus(self, fn):
        """loads a gensim SvmLightCorpus object from disk."""
        corpus = corpora.svmlightcorpus.SvmLightCorpus(fn)
        self.corpus = corpus
        self.has_corpus = True

    def _process_texts(self, texts, generator = False):
        """ Gets vocab and corpus from a list of strings. """
        wordlists = [
            x for x in [self.tokenizer.tokenize(doc) for doc in texts] if x != []
        ]
        self.vocab = corpora.Dictionary(wordlists)
        self.has_vocab = True
        self.corpus = (self.vocab.doc2bow(doc) for doc in wordlists)
        if not generator:
            self.corpus = list(self.corpus)
        self.has_corpus = True

    def parse_topics(self, n=5):
        """
        Parses the model's topics into lists of top words, in decreasing
        sorted order of probability under that topic. 
        """
        assert(self.is_trained)
        raw_topics = self._lda_model.print_topics(self._lda_model.num_topics)
        topics = map(lambda x: x.split(' + '), raw_topics)
        return [
            map(
                lambda x: x.split('*')[1], 
                topic[:n]
            ) 
            for topic in topics]

    def fit(self, texts = None, from_loaded = False):
        """fits a model from an iterable of strings (full, unparsed docs). """
        assert((texts is not None) or from_loaded)
        if texts is not None:
            self._process_texts(texts)
        else:
            assert(self.has_vocab and self.has_corpus)
        self._lda_model = ldamodel.LdaModel(
            corpus=self.corpus, 
            id2word=self.vocab,
            num_topics=self.K

        )
        self.is_trained = True

    def doc_topics(self, docs):
        """
        Get the vectors of topic strengths for the given docs (strings). 
        TODO: does this deal with out of vocabulary tokens? NBD. 
        """
        assert(self.has_vocab)
        assert(self.is_trained)
        tknzd = [self.tokenizer.tokenize(doc) for doc in docs]
        bows = [self.vocab.doc2bow(tkns) for tkns in tknzd]
        return [self._lda_model[bow] for bow in bows]

    def save(self, outdir, just_lda=True):
        """ save all files"""
        if not just_lda:
            vocabfn = '/'.join([outdir, 'vocab_' + name + '.dict'])
            corpusfn = '/'.join([outdir, 'corpus_' + name + '.svmlight'])
            self.vocab.save(vocabfn)
            corpora.SvmLightCorpus.serialize(corpusfn, self.corpus)
        ldafn = '/'.join([outdir, 'lda_' + name])
        self.lda.save(ldafn)

    def visualize(self, outfn):
        if self.has_viz_data:
            pyLDAvis.save_html(self.vis_data, outfn)
            return
        assert(self.has_vocab and self.has_corpus)
        assert(self.is_trained)
        self.vis_data = prepare(self._lda_model, self.corpus, self.vocab)
        self.has_viz_data = True
        pyLDAvis.save_html(self.vis_data, outfn)

    def export(self, outdir, topic_docs = None):
        """ 
        Produce a "model report". 
        Export  parsed topics, doc topics, and visualizatoin.
        topic_docs should be a tuple (pnos, texts) if not None.
        """
        parsed_topics_fn = outdir+'/parsed_topics_'+self.name+'.csv'
        parsed_topics = self.parse_topics()
        with open(parsed_topics_fn, 'wb') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(['topic index', 'top words'])
            for i,t in enumerate(parsed_topics):
                writer.writerow([i]+t)
        if topic_docs is not None:
            doc_tops_fn = outdir+'/doc_topics_'+self.name+'.csv'
            pnos,texts = topic_docs
            doc_tops = self.doc_topics(texts)
            with open(doc_tops_fn, 'wb') as outfile:
                writer = csv.writer(outfile)
                writer.writerow(['pno', 'top 10 topics'])
                for pno,dts in zip(pnos, doc_tops):
                    writer.writerow([pno]+dts)
        visualize_fn = outdir+'/vis'+self.name+'.png'
        self.visualize(visualize_fn)

def tstr():
    db = get_mock()
    n_test = 10
    K=5
    fields = ['_id', 'patText']
    nulls = [None, '']
    pnos, texts = get_fields_unordered(db.pat_text, fields, nulls, n_test)
    lda = MyLda(K, 'tester')
    lda.fit(texts)
    return pnos,texts,lda

def full_pipeline(db, n_topics, out_dir, limit=100, name = None):
    print "Getting texts..."
    fields = ['_id', 'patText']
    nulls = [None, '']
    pnos,texts = get_fields_unordered(
        db.pat_text,
        fields, nulls, limit
    )
    ldamodel = MyLda(K,name)
    print "Fitting model..."
    ldamodel.fit(texts)
    print "Saving model..."
    ldamodel.save(outdir)
    print "exporting summary stats..."
    ldamodel.export(outdir)
    
def pipeline_with_provided_corpus(db, n_topics, out_dir, vocabfn, corpusfn, 
                                  limit=100):
    print "Getting texts..."
    fields = ['_id', 'patText']
    nulls = [None, '']
    pnos,texts = get_fields_unordered(
        db.pat_text,
        fields, nulls, limit
    )
    ldamodel = MyLda(K,name)
    print "loading corpus and vocabulary..."
    ldamodel.load_vocab(vocabfn)
    ldamodel.load_corpus(corpusfn)
    print "Fitting model..."
    ldamodel.fit(from_loaded=True)
    print "Saving model..."
    ldamodel.save(outdir)
    print "exporting summary stats..."
    ldamodel.export(outdir)
    pass

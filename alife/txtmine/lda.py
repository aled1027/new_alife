# utilities for running LDA on our patent database. 
from gensim.models import ldamodel
from gensim import corpora
from pyLDAvis.gensim import prepare
from alife.util.dbutil import get_texts
from alife.mongomock import get_mock
import pyLDAvis


class MyLda(object):
    def __init__(self, n_topics, name=None):
        self.K = n_topics
        assert(type(name) == str)
        if not name:
            self.name = 'lda_'+str(K)
        else:
            self.name = name
        self.has_vocab = False
        self.has_corpus = False
        self.is_trained = False
        
    def _load_vocab(self, fn):
        """loads a gensim vocab.dict object from disk."""

        # vocab = corpora.Dictionary.load(fn)
        # self.vocab = vocab
        # self.has_vocab = True
        pass

    def _load_corpus(self, fn):
        """loads a gensim SvmLightCorpus object from disk."""
        pass

    def _process_wordlists(self, wordlists):
        """ Gets vocab and corpus from wordlists. """
        # self.vocab = corpora.Dictionary(wordlists)
        # self.corpus = [self.vocab.doc2bow(doc) for doc in wordlists]
        pass

    def _parse_topics(self):
        # assert(self.is_trained)
        # do the thing...
        pass

    def fit(self, wordlists = None, from_loaded = False):
        assert(wordlists or from_loaded)
        """fits a model from an iterable of wordlists. """
        # if wordlists:
        #    self._process_wordlists(wordlists)
        # else:
        #     assert(self.has_vocab and self.has_corpus)
        # self._lda_model = ldamodel.LdaModel(self.corpus, self.vocab)
        # self.is_trained = True
        pass

    def save(self, outdir, just_lda=True):
        """ save all files"""
        # if not just_lda:
        #    vocabfn = '/'.join([outdir, 'vocab_' + name])
        #    corpusfn = '/'.join([outdir, 'corpus_' + name])
        #    save(vocabfn, vocab)
        #    save(corpusfn, corpus)
        # ldafn = '/'.join([outdir, 'lda_' + name])
        # save(ldafn, self._lda)
        pass

    def export(self, outdir):
        """ Export parsed model output. E.g. parsed topics, doc topics..."""
        pass

    def visualize(self, outfn = None):
        # assert(self.has_vocab and self.has_corpus)
        # assert(self.is_trained)
        # self.vis_data = prepare(self._lda_model, self.corpus, self.vocab)
        # if outfn:
        #    pyLDAvis.save_html(self.vis_data, outfn)

def test():
    db = get_mock()
    print "Getting texts..."
    texts = util.get_texts(db, 'pat_text')[:100]
    K = 20
    lda = MyLda(K)
    print "fitting lda..."
    lda.fit(texts)
    print "saving data..."
    lda.save('')
    print "exporting parsed model output..."
    lda.export('')
    print "exporting d3 visualization..."
    lda.visualize('')

    

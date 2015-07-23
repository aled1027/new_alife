from alife.mockdb import get_mock
from alife.txtmine import lda
from alife.util.dbutil import get_fields_unordered
import unittest
import os

_this_dir = os.path.dirname(os.path.realpath(__file__))

class TestLda(unittest.TestCase):
    def setUp(self):
        self.db = get_mock()
        self.pat_coll = self.db.pat_text
        self.K = 5
        self.n_docs = 50
        data_dir = '/'.join([_this_dir, 'data'])
        self.out_dir = '/'.join([_this_dir, 'test_output'])
        self.stored_vocab_fn = '/'.join([data_dir, 'test_vocab.dict'])
        self.stored_corpus_fn = '/'.join([data_dir, 'test_corpus.svmlight'])
        self.visualize_fn = '/'.join([data_dir, 'test_vis.png'])
        fields = ['_id', 'patText']
        nulls = [None, '']
        self.pnos, self.texts = get_fields_unordered(
            self.pat_coll,
            fields, nulls, self.n_docs
        )
        self.model = lda.MyLda(self.K, 'tester')

        
    def testProcessWordlists(self):
        self.model._process_texts(self.texts)
        assert(self.model.has_vocab and self.model.has_corpus)
        self.assertEqual(self.n_docs, len(list(self.model.corpus)))

    def testFitsGivenData(self):
        self.model.fit(self.pnos, self.texts)
        self.assertTrue(self.model.is_trained)

    def testLoadsVocab(self):
        self.model.load_vocab(self.stored_vocab_fn)
        self.assertTrue(self.model.has_vocab)
        self.assertTrue(self.model.vocab is not None)
    
    def testLoadsCorpus(self):
        self.model.load_corpus(self.stored_corpus_fn)
        self.assertTrue(self.model.has_corpus)
        self.assertTrue(self.model.corpus is not None)

    def testFitsLoadedData(self):
        self.model.load_vocab(self.stored_vocab_fn)
        self.model.load_corpus(self.stored_corpus_fn)
        self.model.fit(pnos=None, from_loaded = True)
        self.assertTrue(self.model.is_trained)

    def testParseTopics(self):
        self.model.fit(self.pnos, self.texts)
        topics = self.model.parse_topics()
        print topics
        self.assertEqual(len(topics), self.K)
        
    def testDocTopics(self):
        self.model.fit(self.pnos, self.texts)
        doc_topics = self.model.doc_topics(self.texts)
        for p,t in zip(self.pnos, doc_topics):
            print p,t
        self.assertEqual(len(doc_topics),self.n_docs)
        
    def testVisualize(self):
        self.model.fit(self.pnos, self.texts)
        self.model.visualize(self.visualize_fn)
        pass

    def testExport(self):
        self.model.fit(self.pnos, self.texts)
        self.model.export(self.out_dir, topic_docs = (self.pnos, self.texts))
        # TODO: assert that certain files exist, have certain length, etc...

    def testFullPipeline(self):
        lda.full_pipeline(self.db, self.K, self.out_dir, self.n_docs, 'fulltst')

    def testPipelineWithProvidedCorpus(self):
        vocab = lda.load_vocab(self.stored_vocab_fn)
        corpus = lda.load_corpus(self.stored_corpus_fn)
        lda.pipeline_with_provided_corpus(
            self.db, self.K, self.out_dir, 
            self.stored_vocab_fn, self.stored_corpus_fn,
            self.n_docs
        )
        

    

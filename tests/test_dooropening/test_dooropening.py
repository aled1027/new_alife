import unittest
from alife.mockdb import get_mock
from alife.dooropening import reach

# TODO - I need db.traits to have better coverage....
class TestParentChildTraitDistance(unittest.TestCase):
    def setUp(self):
        self.db = get_mock()
        self.n_test = 10
        self.family_docs = self.db.traits.find().limit(self.n_test)

class TestReachComputation(unittest.TestCase):
    def setUp(self):
        self.enforcer = lambda x: len(x.get('citedby', [])) > 100
        self.db = get_mock()
        self.n_test = 5
        self.family_docs = self.db.traits.find().limit(self.n_test)
    
    def Test2GenReachTFIDF(self):
        reach.compute_reach(
            trait='tf-idf', db = self.db, n_gens = 2, family = self.family_docs,
            enforce_func = self.enforcer
        )

    def Test2GenReachW2V(self):
        reach.compute_reach(
            trait='w2v', db = self.db, n_gens = 2, family = self.family_docs,
            enforce_func = self.enforcer
        )

    """
    # NOT READY YET
    def Test2GenReachLDA(self):
        reach.compute_reach(
            trait='lda', db = self.db, n_gens = 2, family = self.family_docs,
            enforce_func = self.enforcer
        )
    """

    def Test5GenReachTFIDF(self):
        reach.compute_reach(
            trait='tf-idf', db = self.db, n_gens = 5, family = self.family_docs,
            enforce_func = self.enforcer
        )

    def Test5GenReachW5V(self):
        reach.compute_reach(
            trait='w2v', db = self.db, n_gens = 5, family = self.family_docs,
            enforce_func = self.enforcer
        )

    """
    # NOT READY YET
    def Test5GenReachLDA(self):
        reach.compute_reach(
            trait='lda', db = self.db, n_gens = 5, family = self.family_docs,
            enforce_func = self.enforcer
        )
    """

    def Test2GenTraitVarianceTFIDF(self):
        reach.compute_trait_variance(trait='tf-idf', n_gens = 2, db=self.db, 
                                     family = self.family_docs)


    def Test2GenTraitVarianceW2V(self):
        reach.compute_trait_variance(trait='w2v', n_gens = 2, db=self.db, 
                                     family = self.family_docs)

    """
    # Not ready yet.
    def Test2GenTraitVarianceLDA(self):
        reach.compute_trait_variance(trait='lda', n_gens = 2, db=self.db, 
                                     family = self.family_docs)
    """

    # Not ready yet.
    def Test5GenTraitVarianceTFIDF(self):
        reach.compute_trait_variance(trait='tf-idf', n_gens = 5, db=self.db, 
                                     family = self.family_docs)

    
    def Test5GenTraitVarianceW2V(self):
        reach.compute_trait_variance(trait='w2v', n_gens = 5, db=self.db, 
                                     family = self.family_docs)

    """
    # Not ready yet.
    def Test5GenTraitVarianceLDA(self):
        reach.compute_trait_variance(trait='lda', n_gens = 5, db=self.db, 
                                     family = self.family_docs)
    """



        

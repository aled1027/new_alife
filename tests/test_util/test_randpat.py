import unittest
from alife.util.randpat import PatentSampler
from alife.mockdb import get_mock

class TestSampler(unittest.TestCase):
    def setUp(self):
        self.db = get_mock()

    def testPatnsWorks(self):
        sampler = PatentSampler(self.db, 'patns')
        sampler.sample(1)

    def testCiteNetWorks(self):
        sampler = PatentSampler(self.db, 'cite_net')
        sampler.sample(1)

    def testTraitsWorks(self):
        sampler = PatentSampler(self.db, 'traits')
        sampler.sample(1)

    def testTraitsWorks(self):
        sampler = PatentSampler(self.db, 'pat_text')
        sampler.sample(1)
    
    def testTraitsWorks(self):
        sampler = PatentSampler(self.db, 'just_cites')
        sampler.sample(1)
        
if __name__ == '__main__':
    unittest.main()

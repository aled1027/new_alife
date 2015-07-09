#tests for dbutil. 
import unittest
from alife.mockdb import get_mock
from alife.util import dbutil

class TestGetFieldsUnordered(unittest.TestCase):
    self.db = get_mock()
    self.n_test = 10

    def testGetFieldsPatns(self):
        fields = ['pno', 'isd', 'title']
        nulls = [None,None,'']
        fields = dbutil.get_fields_unordered(self.db.patns, fields, nulls, self.n_test)
        self.assertEqual(fields.shape, (3,self.n_test))

    def testGetFieldsTraits(self):
        fields = ['_id', 'doc_vec', 'rawcites', 'citedby']
        nulls = [None, [0 for _ in range(300)], [], []]
        fields = dbutil.get_fields_unordered(self.db.traits, fields, nulls, self.n_test)
        self.assertEqual(fields.shape, (4,self.n_test))

class TestCrawlLineage(unittest.TestCase):
    self.db = get_mock()
    self.n_test = 2
    self.pnos_test = dbutil.get_fields_unordered(self.db.patns, ['pno'], [0], 
    self.n_test)

    def testCrawl2Gens(self):
        for pno in self.pnos_test:
            dbutil.crawl_lineage(self.db, pno, n_generations = 2)

if __name__ == '__main__':
    unittest.main()



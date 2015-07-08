#tests for dbutil. 
import unittest
from alife.mockdb import get_mock
from alife.util import dbutil

"""
class TestParallelMap(unittest.TestCase):
    def setUp(self):
        self.mockdb = get_mock()
    
    def testAppliesFuncToAllDocs(self):
        enforce_func = lambda x: 'pno' in x
        def test_func(doc):
            return {'$set': {'dummy_field': 'yay!'}}
        dbutil.parallelMap(test_func, self.mockdb.patns, 'pno', enforce_func)
        self.assertEqual(self.mockdb.patns.find({'dummy_field': 'yay!'}).count(), 1000)
"""

if __name__ == '__main__':
    unittest.main()

# tests the stoplists loader. 

import unittest
from alife.txtmine import stoplists

class TestStopList(unittest.TestCase):
    
    def test_has_my_stoplists(self):
        self.assertTrue(stoplists.load_stoplist('english') != None)
        self.assertTrue(stoplists.load_stoplist('patents') != None)

    def test_not_found_behavior(self):
        with self.assertRaises(RuntimeError):
            stoplists.load_stoplist('Banasns')

if __name__ == '__main__':
    unittest.main()

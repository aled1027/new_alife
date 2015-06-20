# tests the low level text mining utils

import unittest
from alife.txtmine import util

class TestLowLevelTxtUtils(unittest.TestCase):
    def setUp(self):
        self.word = 'b1gd@wg!'
        self.sentence = 'the       the the what it is, Double-beazle?b12890)(*????'
        
    def test_my_split(self):
        self.assertTrue('-' not in util.mysplit(self.sentence))
        self.assertTrue(' ' not in util.mysplit(self.sentence))
        self.assertTrue('' not in util.mysplit(self.sentence))

if __name__ == '__main__':
    unittest.main()
        
        

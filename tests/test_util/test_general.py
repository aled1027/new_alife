# tests the code in alife.util.general
import unittest
from alife.util import general

class test_take(unittest.TestCase):
    def setUp(self):
        self.test_list = range(10)

    def test_empty_list(self):
        self.assertEqual(general.take(10,[]), [])

    def test_take_zero(self):
        self.assertEqual(general.take(0, [1,2,3]), [])

    def test_length_preserved(self):
        self.assertEqual(len(general.take(5, self.test_list)), 5)
        
    def test_disallows_negative(self):
        with self.assertRaises(AssertionError):
            general.take(-10, self.test_list)
            
if __name__ == '__main__':
    unittest.main()

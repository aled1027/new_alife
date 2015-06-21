#tests for dbutil. 
import unittest
from alife.util import dbutil
from pymongo import MongoClient

#global
DB = MongoClient().patents

class TestGetText(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()

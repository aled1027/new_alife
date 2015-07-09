import unittest
from alife.mockdb import get_mock()
from alife.dooropening import reach

# TODO - I need db.traits to have better coverage....

class TestParentChildTraitDistance(unittest.TestCase):
    self.db = get_mock()
    self.n_test = 10
    self.family_docs = self.db.traits.find().limit(self.n_test)
    
    def Test
    

# This module provides a random sampler from each collection.
from bson.objectid import ObjectId # crap, we have old pymongo. Need to bring this up to date. 
from alife.util.general import objid_to_int, int_to_objid
from alife.mockdb import get_mock
from alife.data import load_keymap
from pymongo import MongoClient
import numpy as np
    
def _id_type(collection):
    """ Returns the type of the id field for the collection. *Assumed to be constant accros collection!*"""
    return type(collection.find_one({},{'_id':1})['_id'])

class PatentSampler(object):
    def __init__(self, db, collection_name):
        assert(collection_name in db.collection_names())
        self.collection = db[collection_name]
        self._id_type = _id_type(self.collection)
        self._keymap = load_keymap(collection_name)
        
    def _rand_ids(self, n, replace=False):
        mx = len(self._keymap)
        if replace:
            indices = np.random.randint(low=0,high=mx,size=(n,))
        else:
            indices = np.random.choice(range(mx),n)
        return self._keymap[indices]

    def sample(self, n, replace=False, fields=None):
        ids = list(self._rand_ids(n, replace))
        if self._id_type == ObjectId:
            ids = map(int_to_objid, ids)
        if fields is not None:
            return self.collection.find({'_id': {'$in': ids}}, {field: 1 for field in fields})
        else:
            return self.collection.find({'_id': {'$in': ids}})
            
def test():
    db = MongoClient().patents
    sampler = PatentSampler(db, 'patns')
    return sampler

if __name__ == '__main__':
    sampler = test()
    

# This module provides a random sampler from each collection.
from bson.objectid import ObjectId # crap, we have old pymongo. Need to bring this up to date. 
from alife.util.general import objid_to_int, int_to_objid
from alife.mockdb import get_mock
from alife.data import load_keymap
from pymongo import MongoClient
from random import randrange


#def _minid(collection):
#    """ Get the minimum value of the _id field accross the collection. """
#    return list(collection.find().sort('_id',1).limit(1))[0]['_id']

#def _maxid(collection):
#    """ Get the maximum value of the _id field accross the collection. """
#    return list(collection.find().sort('_id',-1).limit(1))[0]['_id']
    
def _id_type(collection):
    """ Returns the type of the id field for the collection. *Assumed to be constant accros collection!*"""
    return type(collection.find_one({},{'_id':1})['_id'])

#"""
#def n_randrange(low,high, n):
    # Draw a random sample n integers, with replacement, using random.randrange
#    return [randrange(low,high) for _ in xrange(n)]
#"""

class PatentSampler(object):
    def __init__(self, db, collection_name):
        assert(collection_name in db.collection_names())
        self.coll = db[collection_name]
        self._id_type = _id_type(collection)
        self._keymap = load_keymap(collection_name)
        
    def _rand_ids(self, n, replace=False):
        mx = len(self._keymap)
        if replace:
            indices = np.random.randint(low=0,high=mx,size=(n,))
        else:
            indices = np.random.choice(range(mx),n)
        return self._keymap[indices]

    def sample(self.n, replace=False):
        ids = self._rand_ids(n, replace)
        return self.collection.find({'_id': {'$in': ids}})
            
def test():
    db = get_mock()
    sampler = PatentSampler(db.patns)
    n_sample = 10
    s = sampler.sample(n_sample)
    print "n_sample: {}, len(s): {}".format(n_sample, len(s))
    return sampler
    

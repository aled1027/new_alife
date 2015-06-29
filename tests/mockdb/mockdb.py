import os
import unittest
import mongomock as mm

#global
data_dir = '/'.join([os.path.dirname(os.path.realpath(__file__)), 'data'])
db_dumps = {'patns': '/'.join([data_dir, 'mock_patns.p'])}

class Mockdb(object):
    def __init__(self, coll_name):
        if coll_name not in db_dumps:
            raise RuntimeError('Collection {} not currently mocked up'.format(coll_name))
        else:
            dumpfn = db_dumps[coll_name]
            self.coll = mm.Connection().db.coll
            self.coll.restore(dumpfn)
    

import os
import unittest
import mongomock as mm

#global
data_dir = '/'.join([os.path.dirname(os.path.realpath(__file__)), 'data'])
db_dumps = {
    'patns': '/'.join([data_dir, 'mock_patns.p']),
    'cite_net': '/'.join([data_dir, 'mock_cite_net.p']),
    'just_cites': '/'.join([data_dir, 'mock_just_cites.p']),
    'pat_text': '/'.join([data_dir, 'mock_pat_text.p']),
    'corpusDict': '/'.join([data_dir, 'mock_corpusDict.p']),
}

def get_mock(coll_names=db_dumps.keys()):
    """
    Returns a pointer to a mock mongodb Database object,
    with the given collections loaded. 
    """
    db = mm.Connection().db
    for coll_name in coll_names:
        if coll_name not in db_dumps:
            raise RuntimeError('Collection {} not currently mocked up. Supported mock collections: {}'.format(coll_name, db_dumps.keys()))
        else:
            dumpfn = db_dumps[coll_name]
            db[coll_name].restore(dumpfn)
    return db
    

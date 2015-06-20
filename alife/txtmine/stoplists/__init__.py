# to be initialized whenever alife.txtmine.stoplists is imported

import os

# global
THISDIR = os.path.dirname(os.path.realpath(__file__))
STOPLISTS = {'english': 'englishStop.txt', 'patents': 'patentStop.txt'}

def load_stoplist(name):
    """ 
    returns a list of stopwords with the given name.
    """
    if name not in STOPLISTS:
        raise RuntimeError(
            "Sorry, I don't have that stoplist. My stoplists are {}".format(STOPLISTS)
        )
    fn = '/'.join([THISDIR, STOPLISTS[name]])

    with open(fn, 'r') as infile:
        out = set(infile.read().split('\n'))
    return list(out)
    
    

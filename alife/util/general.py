# General utility functions. 

from itertools import islice
import cPickle

def take(n, iterable):
    """
    Take the first n items from an iterable data structure as a list.
    If n is more than the number of items in the iterable, just 
    return all of them. 
    """
    assert(n >= 0)
    out = (x for x in islice(iterable, n))
    return list(islice(iterable, n))

def save_dict(filename, dictionary):
    """
    Pickle and save a python dictionary at the given location on the filesystem.
    """
    with open(filename, 'wb') as outfile:
        cPickle.dump(dictionary, outfile)

def load_dict(filename):
    """
    Load a pickled python dictionary from the given location on the filesystem.
    """
    with open(filename, 'rb') as infile:
        return cPickle.load(infile)

# General utility functions. 

from itertools import islice
import cPickle
import numpy as np

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

def cosine_dist(v1,v2):
    """
    Computes the cosine distance between two vectors,
    which is 1 - the cosine of the angle between them. 
    Recall that <v1,v2> = ||v1|| * ||v2|| * cos(theta)
    """
    cos_ang = np.dot(v1,v2)/(np.linalg.norm(v1)*np.linalg.norm(v2))
    return 1-cos_ang

def euclidean_dist(v1,v2):
    return np.linalg.norm(v1-v2)

def normalize(vector):
    """
    Normalize a vector so that its components sum to 1. 
    """
    return vector/np.linalg.norm(vector)

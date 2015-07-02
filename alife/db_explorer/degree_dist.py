# Measure the in/out degree distributions. 

from pymongo import MongoClient
from alife.mockdb import get_mock
import numpy as np
import matplotlib.pyplot as plt

def _mylen(x):
    """
    Return the length of x if you can. Otherwise return -1. This is because
    0 length is meaningful for our purposes, and we wish to have a different error value. 
    """
    try:
        return len(x)
    except:
        return -1

def all_in_degrees(db, limit = 100):
    """
    Returns a numpy array of in-degrees for each patent.
    """
    if limit is not None:
        pats = db.cite_net.find().limit(limit)
    else:
        pats = db.cite_net.find()
    in_degrees = np.array([_mylen(pat.get('citedby', None)) for pat in pats])
    return in_degrees

def all_out_degrees(db, limit):
    """
    Returns a numpy array of out-degrees for each patent.
    """
    if limit is not None:
        pats = db.cite_net.find().limit(limit)
    else:
        pats = db.cite_net.find()
    out_degrees = np.array([_mylen(pat.get('rawcites', None)) for pat in pats])
    return out_degrees
    
def test():
    db = get_mock()
    n = 750
    in_degs, out_degs = all_in_degrees(db, n), all_out_degrees(db, n)
    f,(ax1, ax2) = plt.subplots(1,2,sharey=True)
    ax1.hist(in_degs, bins=30)
    ax1.set_xlabel('In-Degree')
    ax2.hist(out_degs, bins=30)
    ax2.set_xlabel('Out-Degree')
    plt.suptitle('Degree Distributions')
    return in_degs, out_degs

def main():
    db = MongoClient().patents
    in_degs = all_in_degrees(db, limit=None)
    out_deg = all_out_degrees(db, limit=None)
    f,(ax1, ax2) = plt.subplots(1,2,sharey=True)
    ax1.hist(in_degs, bins=30)
    ax1.set_xlabel('In-Degree')
    ax2.hist(out_degs, bins=30)
    ax2.set_xlabel('Out-Degree')
    plt.suptitle('Degree Distributions')
    plt.savefig('degree_distributions.png')
    


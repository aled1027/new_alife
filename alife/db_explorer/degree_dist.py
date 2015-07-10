# Measure the in/out degree distributions. 

from pymongo import MongoClient
from alife.mockdb import get_mock
from alife.util.general import pickle_obj, load_obj
from alife.util.dbutil import get_fields_unordered as get_fields
from collections import Counter
import matplotlib.pyplot as plt

def in_and_out_counts(db, limit=None):
    inctr, outctr = Counter(), Counter()
    incites, outcites = get_fields(db.cite_net, ['citedby', 'rawcites'], [[],[]], limit)
    inctr.update(map(len, incites))
    outctr.update(map(len, outcites))
    return inctr, outctr
    
def test():
    db = get_mock()
    in_deg_counts, out_deg_counts = in_and_out_counts(db, 100)
    f,(ax1, ax2) = plt.subplots(1,2,sharey=True)
    f.set_size_inches(18.5, 10.5)
    ax1.hist(in_deg_counts.keys(), weights=in_deg_counts.values(), bins=20)
    ax1.set_xlabel('In-Degree')
    ax1.set_ylabel('Count')
    ax2.hist(out_deg_counts.keys(), weights=out_deg_counts.values(), bins=20)
    ax2.set_xlabel('Out-Degree')
    ax2.set_ylabel('Count')
    plt.suptitle('Degree Distributions')
    plt.savefig('degree_distributions_test.png')

def main():
    db = MongoClient().patents
    in_deg_counts, out_deg_counts = in_and_out_counts(db, None)
    pickle_obj('in_deg_counts.p', dict(in_deg_counts))
    pickle_obj('out_deg_counts.p', dict(out_deg_counts))
    f,(ax1, ax2) = plt.subplots(1,2,sharey=True)
    f.set_size_inches(18.5, 10.5)
    ax1.hist(in_deg_counts.keys(), weights=in_deg_counts.values(), bins=100)
    ax1.set_xlabel('In-Degree')
    ax1.set_ylabel('Count')
    ax2.hist(out_deg_counts.keys(), weights=out_deg_counts.values(), bins=100)
    ax2.set_xlabel('Out-Degree')
    ax2.set_ylabel('Count')
    plt.suptitle('Degree Distributions')
    plt.savefig('degree_distributions_test.png')

if __name__ == '__main__':
    main()
    


# Get (and plot) a histogram for dooropening stats. 

import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from pymongo import MongoClient
from alife.mockdb import get_mock
from alife.util.dbutil import get_fields_unordered

def test():
    #    avg_ctr,sum_ctr = Counter(), Counter() # not used, actually. Done in plt.hist
    db = MongoClient().patents
    fields = ["2_gen_avg_dist_w2v", "2_gen_sum_dist_w2v"]
    null_vals = [-2,-2]
    # Get lists of each value of the 'avg' and 'sum' distance resp.
    print "Getting data..."
    avgs,sums = get_fields_unordered(
        db.traits, fields, null_values = null_vals,limit=100
    )
    print "Making plots..."
    fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
    fig.set_size_inches(18.5,10.5)
    ax1.hist(sums,bins=20)
    ax1.set_xlabel('word2vec total distance (1-cosine similarity)')
    ax1.set_ylabel('Counts')
    ax1.set_title('Histogram of total Word2vec parent-child distance (1 generation)')

    ax2.hist(avgs,bins=20)
    ax2.set_xlabel('word2vec average distance (1-cosine similarity)')
    ax2.set_ylabel('Counts')
    ax2.set_title('Histogram of avergae Word2vec parent-child distance (1 generation)')
    plt.show()
    

def main(show=True, savefn = None):
#    avg_ctr,sum_ctr = Counter(), Counter() # not used, actually. Done in plt.hist
    db = MongoClient().patents
    fields = ["2_gen_avg_dist_w2v", "2_gen_sum_dist_w2v"]
    null_vals = [-2,-2]
    avgs,sums = get_fields_unordered(db.traits, fields, null_values = null_vals)
    fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
    fig.set_size_inches(18.5,10.5)
    ax1.hist(sums,bins=100)
    ax1.set_xlabel('word2vec total distance (1-cosine similarity)')
    ax1.set_ylabel('Counts')
    ax1.set_title('Histogram of total Word2vec parent-child distance (1 generation)')

    ax2.hist(avgs,bins=100)
    ax2.set_xlabel('word2vec average distance (1-cosine similarity)')
    ax2.set_ylabel('Counts')
    ax2.set_title('Histogram of avergae Word2vec parent-child distance (1 generation)')
    if savefn:
        plt.savefig(savefn, dpi=100)
    if show:
        plt.show()

if __name__ == '__main__':
    outdir = '/Users/jmenick/Desktop/alife_refactor/output/histograms/dooropening'
    outfn = outdir + 'w2v_sum_avg_1gen.png'
    main(show=False, savefn=outfn)


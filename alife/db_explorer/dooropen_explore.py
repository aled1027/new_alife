# Get (and plot) a histogram for dooropening stats. 

import numpy as np
import matplotlib.pyplot as plt
import sys
from collections import Counter
from pymongo import MongoClient
from alife.mockdb import get_mock
from alife.util.dbutil import get_fields_unordered
from pprint import pprint

def dooropen_hist_w2v_2gen(show=False, savefn=None):
    #    avg_ctr,sum_ctr = Counter(), Counter() # not used, actually. Done in plt.hist
    db = MongoClient().patents
    fields = ["2_gen_avg_dist_w2v", "2_gen_sum_dist_w2v", "2_gen_trait_variance_w2v"]
    null_vals = [-2,-2,-2]
    # Get lists of each value of the 'avg' and 'sum' distance resp.
    print "Getting data..."
    avgs,sums, variances = get_fields_unordered(
        db.traits, fields, null_values = null_vals,limit=None
    )
    avgs = [a for a in avgs if a not in [0,-2]]
    sums = [s for s in sums if s not in [0,-2]]
    variances = [v for v in variances if v not in [0,-2]]
    print "Making plots..."
#    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, sharey=True)
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
    fig.set_size_inches(18.5,10.5)
    ax1.hist(sums,bins=100)
    ax1.set_xlabel('Total Distance')
    ax1.set_ylabel('Count')
    ax1.set_title('Total Parent-Descendant Distance')

    ax2.hist(avgs,bins=100)
    ax2.set_xlabel('Avg. Distance')
    ax2.set_ylabel('Count')
    ax2.set_title('Average Parent-Descendant Distance')

    ax3.hist(variances,bins=100)
    ax3.set_xlabel('Norm of component-wise variance')
    ax3.set_ylabel('Count')
    ax3.set_title('Genealogy Trait Variance')
    plt.title('1-generation Word2Vec Breadth stats')
    if savefn is not None:
        plt.savefig(savefn, dpi=100)
    if show:
        plt.show()

def sorted_dooropen_fields():
    db = MongoClient().patents
    fields = ["_id","2_gen_avg_dist_w2v", "2_gen_sum_dist_w2v", "2_gen_trait_variance_w2v"]
    null_vals = [None, -2,-2,-2]
    # Get lists of each value of the 'avg' and 'sum' distance resp.
    print "Getting data..."
    pnos, avgs,sums, variances = get_fields_unordered(
        db.traits, fields, null_values = null_vals,limit=None
    )
    data = {pno: [a,s,v] for (pno,a,s,v) in zip(pnos, avgs, sums, variances) if a not in [0,-1,-2] and s not in [0,-1,-2] and v not in [0,-1,-2]}
#    avgs = {pno:a for a in avgs if a not in [0,-2]}
#    sums = {pno:s for s in sums if s not in [0,-2]}
#    variances = {pno:v for v in variances if v not in [0,-2]]
    print "Sorting data..." 
    sorted_avgs = [(x, y[0]) for (x,y) in sorted(data.items(), key = lambda x: x[1][0], reverse=True)]
    sorted_sums = [(x, y[1]) for (x,y) in sorted(data.items(), key = lambda x: x[1][1], reverse=True)]
    sorted_vars = [(x, y[2]) for (x,y) in sorted(data.items(), key = lambda x: x[1][2], reverse=True)]
    print "Top 20 patents by total distance: "
    pprint(sorted_sums[:20])
    print "Top 20 patents by average distance: "
    pprint(sorted_avgs[:20])
    print "Top 20 patents by trait variance: "
    pprint(sorted_vars[:20])
    print "done sorting. here ya go."
    return sorted_avgs, sorted_sums, sorted_vars

if __name__ == '__main__':
    sorted_avgs, sorted_sums, sorted_vars = sorted_dooropen_fields()
#    savefn ='dooropen_hist_w2v_2gen.png'
#    if len(sys.argv) == 2:
#        savefn = sys.argv[1]
#    main(show=False, savefn=savefn)


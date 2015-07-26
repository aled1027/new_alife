# Get (and plot) a histogram for dooropening stats. 

import numpy as np
import matplotlib.pyplot as plt
import sys
from collections import Counter
from pymongo import MongoClient
from alife import _allstar_pnos, _normal_pnos
from alife.mockdb import get_mock
from alife.util.dbutil import get_fields_unordered, get_field_generators
from pprint import pprint

def dooropen_hist_micro_overlaid(show=False, savefn=None):
    """ Produces a histogram of the "breadth" dooropening statistics
    we've measured via word2vec traits over 2 generation lineages. 
    """
    #    avg_ctr,sum_ctr = Counter(), Counter() # not used, actually. Done in plt.hist
    db = MongoClient().patents
    fields = ["2_gen_avg_dist_w2v", "2_gen_sum_dist_w2v", "2_gen_trait_variance_w2v"]
    null_vals = [-2,-2,-2]
    # Get lists of each value of the 'avg' and 'sum' distance resp.
    print "Getting data..."
    pnos, avgs,sums, variances = get_fields_unordered(
        db.traits, ['_id']+fields, null_values = [None]+null_vals,limit=None
    )
    avgs = [a for a in avgs if a not in [0,1,-1,-2]]
    print "num averages: {}".format(len(avgs))
    sums = [s for s in sums if s not in [0,-2]]
    print "num sums: {}".format(len(sums))
    # omit outliers
    variances = sorted([v for v in variances if v not in [0,-2]])[:-2000]
    print "num variances: {}".format(len(variances))
    allstar_avgs, allstar_sums, allstar_vars = np.array([
        [db.traits.find_one({'_id': pno}).get(field, -2) for field in fields]
        for pno in _allstar_pnos
    ]).transpose()
    allstar_sums = [s for s in allstar_sums if s not in [0,-2]]
    print "Allstar sums: "
    pprint(allstar_sums)
    allstar_avgs = [a for a in allstar_avgs if a not in [0,-2]]
    print "Allstar avgs: "
    pprint(allstar_avgs)
    allstar_vars = [v for v in allstar_vars if v not in [0,-2]]
    print "allstar variances: "
    pprint(allstar_vars)
    normal_avgs, normal_sums, normal_vars = np.array([
        [db.traits.find_one({'_id': pno}).get(field, -2) for field in fields]
        for pno in _normal_pnos
    ]).transpose()
    normal_sums = [s for s in normal_sums if s not in [0,-2]]
    print "normal sums: "
    pprint(normal_sums)
    normal_avgs = [a for a in normal_avgs if a not in [0,-2]]
    print "normal avgs: "
    pprint(normal_avgs)
    normal_vars = [v for v in normal_vars if v not in [0,-2]]
    print "normal vars: "
    pprint(normal_vars)
    print "Making plots..."
#    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, sharey=True)
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
    fig.set_size_inches(18.5,10.5)
    ax1.hist(sums,bins=50)
    ax1.scatter(allstar_sums, [1000000 for _ in allstar_sums], marker='x', color='red', s=100)
    ax1.scatter(normal_sums, [100000 for _ in normal_sums], marker='x', color='green', s=100)
    ax1.set_yscale('log', nonposy='clip')
    ax1.set_xlabel('Total Distance')
    ax1.set_ylabel('Count (Log Scale)')
    ax1.set_title('Total Parent-Descendant Distance')

    ax2.hist(avgs,bins=50)
    ax2.scatter(allstar_avgs, [215000 for _ in allstar_avgs], marker='x', color='red', s=100)
    ax2.scatter(normal_avgs, [175000 for _ in normal_avgs], marker='x', color='green', s=100)
    ax2.set_ylim(bottom=0)
    ax2.set_xlabel('Avg. Distance')
    ax2.set_ylabel('Count')
    ax2.set_title('Average Parent-Descendant Distance')

    ax3.hist(variances,bins=50)
    ax3.scatter(allstar_vars, [2150000 for _ in allstar_vars], marker='x', color='red', s=100)
    ax3.scatter(normal_vars, [1750000 for _ in normal_vars], marker='x', color='green', s=100)
    ax1.set_yscale('log', nonposy='clip')
    ax3.set_ylim(bottom=0)
    ax3.set_xlabel('Norm of component-wise variance')
    ax3.set_ylabel('Count (Log Scale)')
    ax3.set_title('Genealogy Trait Variance')
    plt.title('1-generation Word2Vec Breadth stats')
    if savefn is not None:
        plt.savefig(savefn, dpi=100)
    if show:
        plt.show()

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
    ax1.set_yscale('log', nonposy='clip')
    ax1.set_xlabel('Total Distance')
    ax1.set_ylabel('Log Count')
    ax1.set_title('Total Parent-Descendant Distance')

    ax2.hist(avgs,bins=100)
    ax2.set_xlabel('Avg. Distance')
    ax2.set_ylabel('Count')
    ax2.set_title('Average Parent-Descendant Distance')

    ax3.hist(variances,bins=100)
    ax3.set_yscale('log', nonposy='clip')
    ax3.set_xlabel('Norm of component-wise variance')
    ax3.set_ylabel('Log Count')
    ax3.set_title('Genealogy Trait Variance')
    plt.title('1-generation Word2Vec Breadth stats')
    if savefn is not None:
        plt.savefig(savefn, dpi=50)
    if show:
        plt.show()

def dooropen_vs_indegree_plots(lim=250000, savefn='test.pdf', show=False):
    db = MongoClient().patents
    trait_fields = ["_id", "2_gen_avg_dist_w2v", "2_gen_sum_dist_w2v", "citedby"]
    trait_nulls = [None, -2, -2, []]
    trait_pnos, avgs, sums, cbs = zip(*list(get_field_generators(
        db.traits, trait_fields, trait_nulls, limit=lim  
    )))
    in_degs = [len(x) for x in cbs]
    _, allstar_avgs, allstar_sums, allstar_cbs = zip(*list([
        [db.traits.find_one({'_id': pno}).get(field, nil) for field,nil in zip(trait_fields, trait_nulls)]
        for pno in _allstar_pnos
    ]))
    _, normal_avgs, normal_sums, normal_cbs = zip(*list((
        [db.traits.find_one({'_id': pno}).get(field, -2) for field,nil in zip(trait_fields, trait_nulls)]
        for pno in _normal_pnos
    )))
    allstar_indegs = [len(cb) for cb in allstar_cbs]
    normal_indegs = [len(cb) for cb in normal_cbs]
    allstar_slopes = [db.patns.find_one({'pno': pno}).get('wave_slope', None)
                      for pno in _allstar_pnos]
    normal_slopes = [db.patns.find_one({'pno': pno}).get('wave_slope', None)
                     for pno in _normal_pnos]
    patn_fields = ["pno", "wave_slope"]
    patn_nulls = [None, None]
    pno_2_slope = {pno: slope for pno,slope in get_field_generators(
        db.patns, patn_fields, patn_nulls, limit=lim
    )}
    slopes_collate = [pno_2_slope.get(pno, None) for pno in trait_pnos]
    assert(len(slopes_collate) == len(avgs) == len(sums))
    # plot total reach vis in-degree.
    f,axarr = plt.subplots(2,2)
    f.set_size_inches(18.5,10.5)
    axarr[0,0].scatter(in_degs,avgs, s=2)
    axarr[0,0].scatter(allstar_indegs, allstar_avgs, marker='x', color='red')
    axarr[0,0].scatter(normal_indegs, normal_avgs, marker='x', color='green')
    axarr[0,0].set_xlabel('In-Degree')
    axarr[0,0].set_ylabel('Average Reach')
    axarr[0,0].set_ylim([0,np.max(allstar_avgs+avgs+normal_avgs)])
    axarr[0,1].scatter(in_degs,sums, s=2)
    axarr[0,1].scatter(allstar_indegs, allstar_sums, marker='x', color='red')
    axarr[0,1].scatter(normal_indegs, normal_sums, marker='x', color='green')
    axarr[0,1].set_xlabel('In-Degree')
    axarr[0,1].set_ylabel('Total Reach')
    axarr[0,1].set_ylim([0,np.max(allstar_sums+sums+normal_sums)])
    axarr[1,0].scatter(slopes_collate, avgs, s=2)
    axarr[1,0].scatter(allstar_slopes, allstar_avgs, marker='x', color='red')
    axarr[1,0].scatter(normal_slopes, normal_avgs, marker='x', color='green')
    axarr[1,0].set_xlabel('wave slope')
    axarr[1,0].set_ylabel('average reach')
    axarr[1,0].set_ylim([0,np.max(allstar_avgs+avgs+normal_avgs)])
    axarr[1,1].scatter(slopes_collate, sums, s=2)
    axarr[1,1].scatter(allstar_slopes, allstar_sums, marker='x', color='red')
    axarr[1,1].scatter(normal_slopes, normal_sums, marker='x', color='green')
    axarr[1,1].set_xlabel('wave slope')
    axarr[1,1].set_ylabel('total reach')
    axarr[1,1].set_ylim([0,np.max(allstar_sums+sums+normal_sums)])
    if savefn is not None:
        plt.savefig(savefn, dpi=50)
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
    dooropen_vs_indegree_plots(lim=None,savefn='markplot.pdf',show=False)
    """
    savefn ='overlay_test.pdf'
    if len(sys.argv) == 2:
        savefn = sys.argv[1]
    dooropen_hist_micro_overlaid(show=False, savefn=savefn)
    """


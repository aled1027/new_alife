# Precomputes the populations at each time step, so that they can be re-used
# (i.e. just computed once) for each trait or trait-type. This is the bottleneck for the GPE calculation that we are attempting to offload. 
from collections import defaultdict
from datetime import datetime, timedelta
from pymongo import MongoClient
from pprint import pprint
from alife.util.general import pickle_obj, pairwise_iter
from alife.util.general import dt_as_str, string_to_dt
from alife.util.general import step_thru_time, step_thru_months, step_thru_qtrs 
from matplotlib import pyplot as plt

_test_outdir = '/Users/jmenick/Desktop/alife_refactor/alife/traits/precomputed_pops_test'
_qtr_outdir = '/Users/jmenick/Desktop/alife_refactor/alife/traits/precomputed_pops_qtrs_fix'
_month_outdir = '/Users/jmenick/Desktop/alife_refactor/alife/traits/precomputed_pops_months'

def len_or_0(x):
    if x is None:
        return 0
    else:
        return len(x)

def n_children(anc_pno, descendant_pop):
    """ Given an ancestor's pno, return how many children it has in the descendant pop."""
    nc = 0
    for d in descendant_pop:
        if anc_pno in d.get('rawcites', []):
            nc += 1
    return nc

def get_new_descendants(db, time_0, time_1, limit = None):
    """ Return all patents that fall between time_0 and time_1. """
    fields = ['rawcites', 'citedby', 'top_tf-idf', 'wordvec_clusters']
    nils = [None, None, [], []]
    projection = {field:1 for field in fields}
    if limit is None or limit <= 0:
        limit = -1
    enforcefunc = lambda x: all(
        x.get(field,nil) != nil for field,nil in zip(fields,nils)
    )
    mapfunc = lambda x: {('n_'+k if k in ['rawcites', 'citedby'] else k):(len_or_0(v) if k in ['rawcites', 'citedby'] else v) for (k,v) in x.items()}
    descendants = (mapfunc(d) for d in db.traits.find({'isd': {'$gte': time_0, '$lt': time_1}}, projection).limit(limit) if enforcefunc(d))
    return descendants

def get_anc_dec_noncum(db, time_0, time_1, limit = None):
    """ Get the ancestral and descendant populations for the period of evolution between time_0 and time_1. 
    Count the number of children non-cumulatively. I.e. the number of children an ancestor has is the number of 
    patents *in the current descendant population* which cite it.
    """
    fields = ['_id', 'rawcites', 'top_tf-idf', 'wordvec_clusters']
    nils = [None, None, [], []]
    projection = {field:1 for field in fields}
    if limit is None or limit <= 0:
        limit = -1
    enforcefunc = lambda x: all(
        x.get(field,nil) != nil for field,nil in zip(fields,nils)
    )
    ancestors = [d for d in db.traits.find({'isd': {'$lt': time_0}}, projection).limit(limit) if enforcefunc(d)]
    descendants = [d for d in db.traits.find({'isd': {'$gte': time_0, '$lt': time_1}}, projection).limit(limit) if enforcefunc(d)]
    def process_anc(anc):
        anc['num_children'] = n_children(anc['_id'], descendants)
            anc.pop('rawcites', None)
        return anc
    def process_doc(dec):
        dec['n_parents'] = len(dec.get('rawcites'))
        dec.pop('rawcites', None)
            return dec
    return (process_anc(anc) for anc in ancestors), (process_dec(dec) for dec in descendants)

def get_anc_dec_mark(db, time_0, time_1, limit = None):
    """ Get the ancestral and descendant populations for the period of evolution between time_0 and time_1. 
    Count the number of children non-cumulatively. I.e. the number of children an ancestor has is the number of 
    patents *in the current descendant population* which cite it. In the fashion mark requested, consider the
    ancestral population to be *only those patents cited in this period*.
    """
    fields = ['_id', 'rawcites', 'top_tf-idf', 'wordvec_clusters']
    nils = [None, None, [], []]
    projection = {field:1 for field in fields}
    if limit is None or limit <= 0:
        limit = -1
    enforcefunc = lambda x: all(
        x.get(field,nil) != nil for field,nil in zip(fields,nils)
    )
    descendants = [d for d in db.traits.find({'isd': {'$gte': time_0, '$lt': time_1}}, projection).limit(limit) if enforcefunc(d)]

    # get the ancestors.
    anc_child_ctr = defaultdict(int)
    for d in descendants:
        for cited_pno in d.get('rawcites', []):
            anc_child_ctr[cited_pno] += 1
    anc_pnos, anc_childcounts = zip(*anc_child_ctr.items())
    ancestors = [db.traits.find_one({'_id': pno}, projection) for pno in anc_pnos]
    ancestors, anc_childcounts = zip(*[a,c for a,c in zip(ancestors,anc_childcounts) if enforcefunc(a) and a is not None])
    del anc_childcounts
    del anc_pnos

    assert(len(ancestors) == len(anc_childcounts))
    for a,c in zip(ancestors, anc_childcounts):
        a['num_children'] = c
        a.pop('rawcites', None)
        
    def process_doc(dec):
        dec['n_parents'] = len(dec.get('rawcites'))
        dec.pop('rawcites', None)
        return dec

    return (anc for anc in ancestors), (process_dec(dec) for dec in descendants)

def dump_descendants_over_time(db, time_pairs, outdir, limit = None, debug = True):
    # also returns a histogram of pop sizes. 
    times = []
    popsizes = []
    for (time_0, time_1) in time_pairs:
        new_descendants = list(get_new_descendants(db, time_0, time_1, limit))
        precompute_doc = {'start': time_0, 'descendants': new_descendants}
        print "number of descendants at time {}: {}".format(time_0, len(new_descendants))
        times.append(time_0)
        popsizes.append(len(new_descendants))
        if debug:
            precompute_doc['descendants'] = len(new_descendants)
            pprint(precompute_doc)
        else:
            popfn = '/'.join([outdir, dt_as_str(time_0)+'.p'])
            print "pickling population for time {} as {}".format(time_0, popfn)
            pickle_obj(popfn, precompute_doc)
    return times, popsizes

def dump_pops_over_time(db, time_pairs, outdir, limit=None, mark = False):
    times = []
    popsizes = []
    for (time_0, time_1) in time_pairs:
        if mark:
            ancestors, new_descendants = map(list, get_anc_dec_mark(db, time_0, time_1, limit))
        else
            ancestors, new_descendants = map(list, get_anc_dec_noncum(db, time_0, time_1, limit))
        precompute_doc = {'start': time_0, 'ancestors': ancestors, 'descendants': new_descendants}
        times.append(time_0)
        popsizes.append((len(ancestors), len(new_descendants)))
        popfn = '/'.join([outdir, dt_as_str(time_0)+'.p'])
            print "pickling population for time {} as {}".format(time_0, popfn)
            pickle_obj(popfn, precompute_doc)
    return times, popsizes

def test(lim=1000):
    db = MongoClient().patents
    outdir = _test_outdir
    start_date = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
    end_date = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', -1).limit(1))[0]['isd']
    print "earliest patent: {}\n latest patent: {}".format(start_date, end_date)
    start_year, start_month = start_date.year, start_date.month
    end_year, end_month = end_date.year, end_date.month
    time_pairs = step_thru_qtrs(start_year, end_year, start_month, end_month)
    dump_descendants_over_time(db, time_pairs, outdir, limit=lim, debug=False)

def main():
    db = MongoClient().patents
    qtr_outdir_noncum = '/Users/jmenick/Desktop/alife_refactor/alife/traits/precomputed_pops_qtrs_noncum'
    qtr_outdir_mark = '/Users/jmenick/Desktop/alife_refactor/alife/traits/precomputed_pops_qtrs_mark'
    start_date = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
    end_date = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', -1).limit(1))[0]['isd']
    print "earliest patent: {}\n latest patent: {}".format(start_date, end_date)
    start_year, start_month = start_date.year, start_date.month
    end_year, end_month = end_date.year, end_date.month
    time_pairs = step_thru_qtrs(start_year, end_year, start_month, end_month)
    times_noncum, sizes_noncum = dump_pops_over_time(db, time_pairs, qtr_outdir_noncum, limit=5000000, mark=False)
    times_mark, sizes_mark = dump_pops_over_time(db, time_pairs, qtr_outdir_mark, limit=5000000, mark=True)
    """
    f = plt.figure()
    f.set_size_inches(20.5, 20.5)
    plt.plot_date(times, sizes)
    plt.xlabel('Time')
    plt.ylabel('Pop Size')
    plt.title('Pop Sizes Per Quarter. Total pats: {}'.format(sum(sizes)))
    plt.savefig('popsizes_over_time.pdf', dpi=100)
    """

if __name__ == '__main__':
    main()


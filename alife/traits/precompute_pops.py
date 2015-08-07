# Precomputes the populations at each time step, so that they can be re-used
# (i.e. just computed once) for each trait or trait-type. This is the bottleneck for the GPE calculation that we are attempting to offload. 
from datetime import datetime, timedelta
from pymongo import MongoClient
from pprint import pprint
from alife.util.general import pickle_obj, pairwise_iter
from alife.util.general import dt_as_str, string_to_dt
from alife.util.general import step_thru_time, step_thru_months, step_thru_qtrs 

_test_outdir = '/Users/jmenick/Desktop/alife_refactor/alife/traits/precomputed_pops_test'
_qtr_outdir = '/Users/jmenick/Desktop/alife_refactor/alife/traits/precomputed_pops_qtrs'
_month_outdir = '/Users/jmenick/Desktop/alife_refactor/alife/traits/precomputed_pops_months'

def get_new_descendants(db, time_0, time_1, limit = None):
    """ Return all patents that fall between time_0 and time_1. """
    fields = ['rawcites', 'citedby', 'top_tf-idf', 'wordvec_clusters']
    nils = [[] for _ in fields] # yep, the nil value is the empty list. 
    projection = {field:1 for field in fields}
    if limit is None or limit <= 0:
        limit = -1
    enforcefunc = lambda x: all(
        x.get(field,nil) != nil for field,nil in zip(fields,nils)
    )
    mapfunc = lambda x: {('n_'+k if k in ['rawcites', 'citedby'] else k):(len(v) if k in ['rawcites', 'citedby'] else v) for (k,v) in x.items()}
    descendants = (mapfunc(d) for d in db.traits.find({'isd': {'$gte': time_0, '$lt': time_1}}, projection).limit(limit) if enforcefunc(d))
    return descendants

def dump_descendants_over_time(db, time_pairs, outdir, limit = None, debug = True):
    for (time_0, time_1) in time_pairs:
        new_descendants = list(get_new_descendants(db, time_0, time_1, limit))
        precompute_doc = {'start': time_0, 'descendants': new_descendants}
        if debug:
            precompute_doc['descendants'] = len(new_descendants)
            pprint(precompute_doc)
        else:
            popfn = '/'.join([outdir, dt_as_str(time_0)+'.p'])
            print "pickling population for time {} as {}".format(time_0, popfn)
            pickle_obj(popfn, precompute_doc)

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
    outdir = _qtr_outdir
    start_date = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
    end_date = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', -1).limit(1))[0]['isd']
    print "earliest patent: {}\n latest patent: {}".format(start_date, end_date)
    start_year, start_month = start_date.year, start_date.month
    end_year, end_month = end_date.year, end_date.month
    time_pairs = step_thru_qtrs(start_year, end_year, start_month, end_month)
    dump_descendants_over_time(db, time_pairs, outdir, limit=5000000, debug=False)

if __name__ == '__main__':
    main()


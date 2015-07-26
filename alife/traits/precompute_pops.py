# Precomputes the populations at each time step, so that they can be re-used
# (i.e. just computed once) for each trait or trait-type. This is the bottleneck for the GPE calculation that we are attempting to offload. 
from datetime import datetime, timedelta
from pymongo import MongoClient
from pprint import pprint
from alife.util.general import pickle_obj
from alife.util.general import dt_as_str, string_to_dt, step_through_time

def get_populations(db, time_0, time_1, time_2, limit=100):
    """ Returns, for given times (time_0, time_1, time_2), an iterable of patent
    documents occuring between time_0 and time_1 time 1 (called 'the new ancestral population'),
    and an iterable of documents occuring between time 1 and time_2 (called 'the descendant population'). The full 
    ancestral population can be determined by accumulating new ancestral populations (but this means you must go in order.)
    This way, we don't need to worry about database queries for 'isd < x' to take forever, which they do, despite
    the traits collection being indexed on issue date and fitting into memory. """
    # get all the traits. 
    fields = ['rawcites', 'citedby', 'top_tf-idf', 'wordvec_clusters']
    nils = [[] for _ in fields] # yep, the nil value is the empty list. 
    projection = {field:1 for field in fields}
    if limit is None:
        limit = -1
    enforcefunc = lambda x: all(
        x.get(field,nil) != nil for field,nil in zip(fields,nils)
    )
    new_ancestors = (a for a in db.traits.find({'isd': {'$gte': time_0, '$lt': time_1}}, projection).limit(limit) if enforcefunc(a))
    descendants = (d for d in db.traits.find({'isd': {'$gte': time_1, '$lt': time_2}}).limit(limit) if enforcefunc(d))
    return new_ancestors, descendants

def dump_populations(db, start, end, outdir, delta=timedelta(days=7),lim=100, debug=True):
    """ Step through time, maintaining the known ancestral population at each time step. Save each 
    set of populations as a pickled dictionary."""
    for (tm1, t, tp1) in step_through_time(start, end):
        new_ancestors, descendants = get_populations(db, tm1, t, tp1, lim)
        precompute_doc = {'_id': tm1, 'new_ancestors': list(new_ancestors), 'descendants': list(descendants)}
        if debug: 
            precompute_doc['new_ancestors'] = len(precompute_doc['new_ancestors'])
            precompute_doc['descendants'] = len(precompute_doc['descendants'])
            pprint(precompute_doc)
        else:
            popfn = '/'.join([outdir, dt_as_str(tm1)+'.p'])
            print "pickling population for time {} as {}".format(tm1, popfn)
            print "#new ancestors: {}, #descendants:{}".format(len(precompute_doc['new_ancestors']), len(precompute_doc['descendants']))
            pickle_obj(popfn, precompute_doc)

def test():
    db = MongoClient().patents
    outdir = '/Users/jmenick/Desktop/alife_refactor/alife/traits/precomputed_pops'
    start_date = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
    end_date = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', -1).limit(1))[0]['isd']
    print "earliest patent: {}\n latest patent: {}".format(start_date, end_date)
    dump_populations(db, start_date, end_date, outdir, lim=50000, debug=True)

def main():
    db = MongoClient().patents
    outdir = '/Users/jmenick/Desktop/alife_refactor/alife/traits/precomputed_pops'
    start_date = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
    end_date = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', -1).limit(1))[0]['isd']
    print "earliest patent: {}\n latest patent: {}".format(start_date, end_date)
    dump_populations(db, start_date, end_date, outdir, lim=5000000, debug=False)

if __name__ == '__main__':
    main()

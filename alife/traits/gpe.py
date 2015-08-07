# Measure the Generalized Price Equation terms for all of our traits and trait types for arbitrary episodes of evolution.
from alife.util.general import timer, load_obj, step_through_time, dt_as_str, pickle_obj
from alife.util.dbutil import get_fields_unordered as get_fields
from alife.mockdb import get_mock
from alife.traits import _trait_info
from alife.traits.plot_gpe import plot_gpe
from pymongo import MongoClient
from datetime import datetime, timedelta
from pprint import pprint
import numpy as np
import logging
import multiprocessing as mp

_log_format = '%(asctime)s : %(levelname)s : %(message)s'
logging.basicConfig(filename='gpe.log',format= _log_format, level=logging.INFO)

_pop_dir = '/Users/jmenick/Desktop/alife_refactor/alife/traits/precomputed_pops_weeks'
_interesting_tfidf_traits = ['hyperlink', 'dna', 'internet', 'mobile',
                          'semiconductor', 'softwar', 'batteri', 'crypto',
                           'video', 'fluroesc', 'diode','prosthet',
                          'network', 'cancer', 'neural',
                          'processor', 'smart', 'sequenc', 'jet', 'droplet', 
                          'graft', 'link', 'tape', 'film','liquid','ribonucleas']
_uninteresting_tfidf_traits = ['results','consists','adjustment',
                           'layers','increase','aligned','zone',
                           'include','indicating','applied',
                           'connects','condition','joined','large',
                           'small','path']
_tfidf_traits = _interesting_tfidf_traits + _uninteresting_tfidf_traits
_docvec_traits = range(200)

def load_pops(start_time, limit = None):
    date_str = dt_as_str(start_time)
    popfn = '/'.join([_pop_dir, date_str+'.p'])
    doc = load_obj(popfn)
    if limit is not None:
        return doc['new_ancestors'], doc['descendants']
    else:
        return doc['new_ancestors'][:limit], doc['descendants'][:limit]

def get_rel_num_children(population, rel_avg = True):
    """
    For a given population (here, list of patent documents), 
    return a list (with an element for each member of the population)
    containing how many children each entity has (optionally, relative)
    to the average number of children. 
    """
    nchilds = np.array([len(doc.get('citedby', [])) for doc in population])
    if not rel_avg:
        return nchilds
    else:
        avg_childs = np.mean(nchilds)
        return nchilds/float(avg_childs)
    
def get_rel_num_parents(population, rel_avg = True):
    """
    For a given population (here, list of patent documents), 
    return a list (with an element for each member of the population)
    containing how many parents each entity has (optionally, relative)
    to the average number of parents. 
    """
    nparents = np.array([len(doc.get('rawcites', [])) for doc in population])
    if not rel_avg:
        return nparents
    else:
        avg_parents = np.mean(nparents)
        return nparents/float(avg_parents)

def get_traits(population, trait_type, trait):
    """
    For a given population, trait type, and trait,
    return an array (with an element for each member of the population)
    whose i^th element indicates whether the i^th member of the population
    has the trait or not. It is binary for now. 
    """
    _,_,_,trait_val = _trait_info[trait_type]
    return np.array([trait_val(doc, trait) for doc in population])

def _cov2(x,y):
    """ Computes the covariance between vectors x and y, 
    except dividing the sum of mean deviations by n rather than by n+1. 
    This is how excel does it, but is not the 'sample covariance', 
    the generally held best estimator for the covariance. We have this function
    to test against Marks' implementation in excel. """
    assert(x.shape==y.shape)
    xbar, ybar = map(np.mean, [x,y])
    s = np.sum([(xi-xbar)*(yi-ybar) for xi,yi in zip(x,y)])
    return float(s)/len(x)

def compute_gpe(childchar, parchar, anc_traits, dec_traits, sample_cov=True):
    """ Computes the Generalized Price Equation for arbitrary vectors. 
    Separates database logic from this computation, so that it's easy to drop in 
    data from arbitrary sources. """
    total = np.mean(dec_traits) - np.mean(anc_traits)
    if sample_cov:
        t1 = np.cov(childchar, anc_traits)[0][1]
        t3 = np.cov(parchar, dec_traits)[0][1]
    else:
        t1 = _cov2(childchar, anc_traits)
        t3 = _cov2(parchar, dec_traits)
    t2 = total - t1 + t3
    return t1,t2,t3

def gpe(time_1, trait_type, trait, limit=None):
    """ Computes the GPE for the given trait on specified populations. """
    ancestors, descendants = load_pops(time_1, limit=limit)
    ancestor_traits = get_traits(ancestors, trait_type, trait)
    descendant_traits = get_traits(descendants, trait_type, trait)
    n_children_rel = get_rel_num_children(ancestors)
    n_parents_rel = get_rel_num_parents(descendants)
    return compute_gpe(n_children_rel, n_parents_rel, ancestor_traits, descendant_traits)

def gpe_multi(time_1, trait_type, traits, limit=None, old_ancestors = []):
    """ Computes the GPE for the given traits on specified populations. """
    new_ancestors, descendants = load_pops(time_1, limit=limit)
    ancestors = old_ancestors + new_ancestors
    n_children_rel = get_rel_num_children(ancestors)
    n_parents_rel = get_rel_num_parents(descendants)
    peqs = {time_1: {}}
    for trait in traits:
        ancestor_traits = get_traits(ancestors, trait_type, trait)
        descendant_traits = get_traits(descendants, trait_type, trait)
        peqs[time_1][trait] = compute_gpe(n_children_rel, n_parents_rel, ancestor_traits, descendant_traits)
    return peqs, new_ancestors

def gpe_multi_threaded(time_1, trait_type, traits, limit=None, old_ancestors = []):
    """ Computes the GPE for the given traits on specified populations. Goes after each trait in parallel. """
    new_ancestors, descendants = load_pops(time_1, limit=limit)
    ancestors = old_ancestors + new_ancestors
    n_children_rel = get_rel_num_children(ancestors)
    n_parents_rel = get_rel_num_parents(descendants)
    peqs = {time_1: {}}
    workQueue = mp.Queue()
    returnQueue = mp.Queue()
    # add each trait to a work queue
    for trait in traits:
        workQueue.put(trait)
    def threadFunc():
        while not workQueue.empty():
            trait = workQueue.get()
            ancestor_traits = get_traits(ancestors, trait_type, trait)
            descendant_traits = get_traits(descendants, trait_type, trait)
            returnQueue.put({trait: compute_gpe(n_children_rel, n_parents_rel, ancestor_traits, descendant_traits)})
    workers = []
    # get the worker threads goin. 
    for i in range(mp.cpu_count()):
        p = mp.Process(target=threadFunc)
        p.start()
        workers.append(p)
    
    # wait for the workers to finish.
    for worker in workers:
        worker.join()

    # Put the values the threads computed into a dict. 
    out_dict = {}
    while not returnQueue.empty():
        out_dict.update(returnQueue.get())
    
    # make sure the dict has the right number of values (one for each trait!)
    assert(len(out_dict)==len(traits))
    return {time_1: out_dict},new_ancestors

def tester_serial():
    db = MongoClient().patents
    oneweek = timedelta(days=7)
    mindate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
    maxdate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', -1).limit(1))[0]['isd']
    trait_type = 'w2v'
    traits = list(set(_docvec_traits))
    old_ancestors = []
    gpes = {}
    for (t1,_,_) in step_through_time(mindate,maxdate,oneweek)[:10]:
        logging.info("computing gpe for time {}".format(t1))
        gpe_dict, new_ancestors = gpe_multi(t1, trait_type, traits, None, old_ancestors)
        gpes[t1] = gpe_dict[t1]
        old_ancestors = old_ancestors + new_ancestors
    return gpes

def benchmark_fn():
    db = MongoClient().patents
    oneweek = timedelta(days=7)
    mindate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
    maxdate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', -1).limit(1))[0]['isd']
    old_ancestors = []
    gpes_tfidf = {}
    gpes_w2v = {}
    for (t1,_,_) in step_through_time(mindate,maxdate,oneweek)[:10]:
        logging.info("computing gpe for time {}".format(t1))
        gpe_dict_tfidf1, new_ancestors = gpe_multi(t1, 'tf-idf', _tfidf_traits, None, old_ancestors)
        gpe_dict_tfidf2, _ = gpe_multi_threaded(t1, 'tf-idf', _tfidf_traits, None, old_ancestors)
        gpe_dict_w2v1, _ = gpe_multi(t1, 'w2v', _docvec_traits, None, old_ancestors)
        gpe_dict_w2v2, _ = gpe_multi_threaded(t1, 'w2v', _docvec_traits, None, old_ancestors)
        assert(sorted(gpe_dict_w2v1.items()) == sorted(gpe_dict_w2v2.items())) # Make sure the multithreaded method returns the same terms.
        assert(sorted(gpe_dict_tfidf1.items()) == sorted(gpe_dict_tfidf2.items())) # Make sure the multithreaded method returns the same terms.
        gpes_tfidf[t1] = gpe_dict_tfidf1[t1]
        gpes_w2v[t1] = gpe_dict_w2v1[t1]
        old_ancestors = old_ancestors + new_ancestors
    return gpes_tfidf, gpes_w2v

def test_tfidf(time_limit=20, pop_limit = 50000):
    """ Runs the GPE calculation on a subset of each population in the time window 1976-2014, for the tf-idf trait 'dna'. """
    db = MongoClient().patents
    oneweek = timedelta(days=7)
    mindate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
    maxdate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', -1).limit(1))[0]['isd']
#    trait_type = 'tf-idf'
#    traits = list(set(_tfidf_traits))
    old_ancestors = []
    gpes = {}
    for (t1,_,_) in step_through_time(mindate,maxdate,oneweek)[:time_limit]:
        logging.info("computing gpe for time {}".format(t1))
        gpe_dict, new_ancestors = gpe_multi(t1, trait_type, traits, pop_limit, old_ancestors)
        gpes[t1] = gpe_dict[t1]
        old_ancestors = old_ancestors + new_ancestors
    return gpes

def test_docvec(time_limit=20, pop_limit = 50000):
    """ Runs the GPE calculation on a subset of each population in the time window 1976-2014, for the tf-idf trait 'dna'. """
    db = MongoClient().patents
    oneweek = timedelta(days=7)
    mindate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
    maxdate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', -1).limit(1))[0]['isd']
    trait_type = 'w2v'
    traits = _docvec_traits
    old_ancestors = []
    gpes = {}
    for (t1,_,_) in step_through_time(mindate,maxdate,oneweek)[:time_limit]:
        logging.info("computing gpe for time {}".format(t1))
        gpe_dict, new_ancestors = gpe_multi(t1, trait_type, traits, pop_limit, old_ancestors)
        gpes[t1] = gpe_dict[t1]
        old_ancestors = old_ancestors + new_ancestors
    return gpes

def main_tfidf():
    """ Runs the GPE calculation on the whole population, for each of a selected bunch of tf-idf traits."""
    db = MongoClient().patents
    oneweek = timedelta(days=7)
    mindate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
    maxdate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', -1).limit(1))[0]['isd']
    trait_type = 'tf-idf'
    traits = list(set(_tfidf_traits))
    old_ancestors = []
    gpes = {}
    for (t1,_,_) in step_through_time(mindate,maxdate,oneweek):
        logging.info("computing gpe for time {}".format(t1))
        gpe_dict, new_ancestors = gpe_multi(t1, trait_type, traits, None, old_ancestors)
        gpes[t1] = gpe_dict[t1]
        old_ancestors = old_ancestors + new_ancestors
    return gpes

def main_docvec():
    """ Runs the GPE calculation for the whole population, for each docvec trait."""
    db = MongoClient().patents
    oneweek = timedelta(days=7)
    mindate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
    maxdate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', -1).limit(1))[0]['isd']
    trait_type = 'w2v'
    traits = _docvec_traits
    old_ancestors = []
    gpes = {}
    for (t1,_,_) in step_through_time(mindate,maxdate,oneweek):
        logging.info("computing gpe for time {}".format(t1))
        gpe_dict, new_ancestors = gpe_multi(t1, trait_type, traits, None, old_ancestors)
        gpes[t1] = gpe_dict[t1]
        old_ancestors = old_ancestors + new_ancestors
    return gpes

def main_both():
    """ Runs the GPE calculation for the whole population, for each docvec trait."""
    db = MongoClient().patents
    oneweek = timedelta(days=7)
    mindate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
    maxdate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', -1).limit(1))[0]['isd']
    old_ancestors = []
    gpes_tfidf = {}
    gpes_docvec = {}
    for (t1,_,_) in step_through_time(mindate,maxdate,oneweek):
        logging.info("computing gpe for time {}, both tf-idf and w2v".format(t1))
        gpe_dict_w2v, new_ancestors = gpe_multi_threaded(t1, 'w2v', _docvec_traits, None, old_ancestors)
        gpe_dict_tfidf, _ = gpe_multi_threaded(t1, 'tf-idf', _tfidf_traits, None, old_ancestors) # multithreading Not worth overhead for tfidf 
        gpes_docvec[t1] = gpe_dict_w2v[t1] # alternatively, use dict.update()
        gpes_tfidf[t1] = gpe_dict_tfidf[t1] # alternatively, use dict.update()
        old_ancestors = old_ancestors + new_ancestors
    return gpes_tfidf, gpes_docvec
    
if __name__ == '__main__':
    gpes_tfidf, gpes_docvec = main_both()
    try:
        pickle_obj('gpes_docvec.p', gpes_docvec)
        pickle_obj('gpes_tfidf.p', gpes_tfidf)
    except:
        logging.info("error.")
        logging.info("docvec gpes:")
        pprint(gpes_docvec)
        logging.info("tfidf gpes.")
        pprint(gpes_tfidf)

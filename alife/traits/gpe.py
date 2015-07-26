# Measure the Generalized Price Equation terms for all of our traits and trait types for arbitrary episodes of evolution.
from alife.util.general import timer, load_obj, step_through_time, dt_as_str
from alife.util.dbutil import get_fields_unordered as get_fields
from alife.mockdb import get_mock
from alife.traits import _trait_info
from pymongo import MongoClient
from datetime import datetime, timedelta
import numpy as np

_pop_dir = '/Users/jmenick/Desktop/alife_refactor/alife/traits/precomputed_pops'

def load_pops(start_time, limit = None):
    date_str = dt_as_str(start_time)
    popfn = '/'.join([_pop_dir, date_str+'.p'])
    doc = load_obj(popfn)
    if limit is not None:
        return doc['ancestors'], doc['descendants']
    else:
        return doc['ancestors'][:limit], doc['descendants'][:limit]

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

def test(time_limit=10, pop_limit = 1000):
    """ Runs the GPE calculation on a subset of each population in the time window 1976-2014, for the tf-idf trait 'dna'. """
    db = MongoClient().patents
    oneweek = timedelta(days=7)
    mindate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
    maxdate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', -1).limit(1))[0]['isd']
    trait_type = 'tf-idf'
    interesting_traits = ['link', 'hyperlink', 'ribonucleas', 'liquid',
                          'semiconductor', 'softwar', 'batteri', 'film', 
                          'tape', 'video', 'crypto', 'fluroesc', 
                          'network', 'cancer', 'internet', 'mobile', 
                          'processor', 'smart', 'sequenc', 'jet', 'droplet', 
                          'graft', 'prosthet', 'dna', ]
    uninteresting_traits = ['results','consists','adjustment',
                           'layers','increase','aligned','zone',
                           'include','indicating','applied',
                           'connects','condition','joined','large',
                           'small','path']
    traits = interesting_traits + uninteresting_traits
    time_limit = 10
    gpes = {}
    for (t1,_,_) in step_through_time(mindate,maxdate,oneweek)[:time_limit]:
        gpes[t1] = gpe_multi(t1, trait_type, traits, pop_limit)[t1]
    return gpes

def main():
    db = MongoClient().patents
    oneweek = timedelta(days=7)
    mindate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
    maxdate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', -1).limit(1))[0]['isd']
    trait_type = 'tf-idf'
    interesting_traits = ['link', 'hyperlink', 'ribonucleas', 'liquid',
                          'semiconductor', 'softwar', 'batteri', 'film', 
                          'tape', 'video', 'crypto', 'fluroesc', 
                          'network', 'cancer', 'internet', 'mobile', 
                          'processor', 'smart', 'sequenc', 'jet', 'droplet', 
                          'graft', 'prosthet', 'dna', ]
    uninteresting_traits = ['results','consists','adjustment',
                           'layers','increase','aligned','zone',
                           'include','indicating','applied',
                           'connects','condition','joined','large',
                           'small','path']
    traits = interesting_traits + uninteresting_traits
    time_limit = 10
    gpes = {}
    old_ancestors = []
    for (t1,_,_) in step_through_time(mindate,maxdate,oneweek):
        gpe_dict, new_ancestors = gpe_multi(t1, trait_type, traits, None, old_ancestors)
        gpes[t1] = gpe_dict[t1]
        old_ancestors = old_ancestors + new_ancestors
    return gpes
    
if __name__ == '__main__':
    gpes = test()


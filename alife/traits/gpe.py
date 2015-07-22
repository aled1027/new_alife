# Measure the Generalized Price Equation terms for all of our traits and trait types for arbitrary episodes of evolution.
from alife.util.general import timer
from alife.util.dbutil import get_fields_unordered as get_fields
from alife.mockdb import get_mock
from alife.traits import _trait_info
from pymongo import MongoClient
from datetime import datetime, timedelta
import numpy as np

def step_through_time(start,end, delta=timedelta(days=7)):
    """ Returns a list of time pairs (start,end) which define 
    endpoints of intervals of length delta (e.g. 1 week). """
    i = 0
    times = []
    _current_time = start + delta
    while _current_time < end:
        nxt = _current_time + delta
        times.append((_current_time, nxt))
        _current_time = nxt
        i += 1
    return times

def get_populations(db, time_1, time_2, trait_type = 'tf-idf', limit=100):
    trait_field, _,_,_ = _trait_info[trait_type]
    fields = [trait_field, 'rawcites', 'citedby']
    nils = [[],[],[]]
    """
    Given two times, get an ancestral population, all those occurring before time 1, 
    and a descendant population, all those occuring between time1 and time2.
    This is the crucial function for making sure the analysis is fast. This is slow 
    even though we have indexed on isd. The solution seems to be to pre-compute these
    populations and store them in mongodb. Key from time to docs with all the traits, citedby,rawcites.
    """
    projection = {field: 1 for field in fields}
    enforcefunc = lambda x: all(x.get(field,nil) != nil for field,nil in zip(fields,nils))
    if limit is not None:
        ancestors = (a for a in db.traits.find({'isd': {'$lt': time_1}}, projection).limit(limit) if enforcefunc(a))
        descendants = (d for d in db.traits.find({'isd': {'$gte': time_1, '$lt': time_2}}).limit(limit) if enforcefunc(d))
    else:
        ancestors = (a for a in db.traits.find({'isd': {'$lt': time_1}}, projection) if enforcefunc(a))
        descendants = (d for d in db.traits.find({'isd': {'$gte': time_1, '$lt': time_2}}) if enforcefunc(d))
    return list(ancestors), list(descendants)

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
    _,_,_,has_trait = _trait_info[trait_type]
    return np.array([has_trait(doc, trait) for doc in population])

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

def gpe(db, time_1, time_2, trait_type, trait, limit=None):
    """ Computes the GPE for the given trait on specified populations. """
    ancestors, descendants = get_populations(db, time_1, time_2, trait_type, limit=limit)
    ancestor_traits = get_traits(ancestors, trait_type, trait)
    descendant_traits = get_traits(descendants, trait_type, trait)
    n_children_rel = get_rel_num_children(ancestors)
    n_parents_rel = get_rel_num_parents(descendants)
    return compute_gpe(n_children_rel, n_parents_rel, ancestor_traits, descendant_traits)

def test(time_limit=10, pop_limit = 1000):
    """ Runs the GPE calculation on a sample population from the 1980s, for the trait 'dna'. """
    db = MongoClient().patents
    oneweek = timedelta(days=7)
    mindate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
    maxdate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', -1).limit(1))[0]['isd']
    trait_type = 'tf-idf'
    trait = 'dna'
    time_limit = 10
    gpes = []
    for (t1,t2) in step_through_time(mindate,maxdate,oneweek)[:time_limit]:
        gpes.append(gpe(db, t1, t2, trait_type, trait, pop_limit))
    return gpes

def main():
    """ Runs the GPE calculation on a sample population from the 1980s, for the trait 'dna'. """
    db = MongoClient().patents
    oneweek = timedelta(days=7)
    mindate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
    maxdate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', -1).limit(1))[0]['isd']
    trait_type = 'tf-idf'
    trait = 'evolv'
    gpes = []
    for (t1,t2) in step_through_time(mindate,maxdate,oneweek):
        gpes.append(gpe(db, t1, t2, trait_type, trait))
    return gpes

if __name__ == '__main__':
    gpes = test()


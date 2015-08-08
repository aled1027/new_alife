# Compute the GPE quickly. I.e. not many weeks. 
import numpy as np
from pymongo import MongoClient
from alife.util.general import step_thru_qtrs, load_obj
from alife.traits.gpe import get_rel_num_children, get_rel_num_parents, get_traits
import multiprocessing as mp

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

def load_pop(start_date):
    fn = '/'.join([_pop_dir, dt_as_str(start_date)+'.p'])
    return load_obj(fn)

def running_avg(xsum, N, new_xs):
    """ Update the mean, given new data. """
    M = len(new_xs)
    return (xsum + np.sum(new_xs))/float(N+M)
    
def running_cov(N, xsum, ysum, dotxy, new_xs, new_ys, ret_avgs = False):
    """ Update the covariance, given new data. """
    M = len(new_xs)
    xs_avg = running_avg(xsum, N, new_xs)
    ys_avg = running_avg(ysum, N, new_ys)
    new_dotxy = np.dot(new_xs, new_ys)
    correction = (N+M)/float(N+M-1)
    new_cov = (dotxy + new_dotxy)/float(N+M-1) - (xs_avg*ys_avg)*correction
    if ret_avgs:
        return new_cov, xs_avg, ys_avg
    else:
        return new_cov

class TemporalGPE(object):
    """
    A class which computes the GPE for a particular trait. 
    """
    def __init__(self, trait_type, trait, anc_pop):
        """
        Initializes a temporal GPE computation with an ancestral pop.
        We begin computing the GPE terms upon receiving a descendant population
        """
        self.i = 0
        self.trait_type = trait_type
        self.trait = trait

        self.anc_N = len(anc_pop)
        _anc_traits = get_traits(anc_pop, self.trait_type, self.trait)
        _anc_children = get_rel_num_children(anc_pop)
        self.anc_trait_sum = np.sum(_anc_traits)
        self.anc_n_children_sum = np.sum(_anc_children)
        self.dot_nc_traits = np.dot(_anc_traits, _anc_children)
        self.prev_t1 = np.cov(_anc_children, _anc_traits)
        self.gpes = []
        
    def update(self, desc_pop):
        desc_M = len(desc_pop)

        # Get the n_children, n_parents, and trait character vectors for the new pop.
        rel_parents = get_rel_num_parents(desc_pop)
        rel_children = get_rel_num_children(desc_pop)
        desc_traits = get_traits(desc_pop, self.trait_type, self.trait)

        # compute the quantities needed for relevant covariances, means.
        desc_trait_sum = np.sum(desc_traits)
        desc_trait_avg = float(desc_trait_sum)/desc_M
        anc_trait_avg = self.anc_trait_sum/float(anc_N)
        t1 = self.prev_t1
        t3 = np.cov(rel_parents, desc_traits)
        gpe_tot = desc_trait_avg - anc_trait_avg
        t2 = gpe_tot + t3 - t1
        self.gpes.append(t1, t2, t3, gpe_tot)
        
        # update prev_t1 and running sums, counts, dot products
        self.prev_t1 = running_cov(self.anc_N, self.anc_n_children_sum, self.anc_trait_sum, self.dot_nc_traits, rel_children, desc_traits)
        self.dot_nc_traits += np.dot(desc_traits, rel_children)
        self.anc_N += desc_M
        self.anc_trait_sum += desc_trait_sum
        self.anc_n_children_sum += np.sum(rel_children)
        self.i += 1

def compute_gpe():
    pass

def test():
    tfidf_traits = _interesting_tfidf_traits + _uninteresting_tfidf_traits
    docvec_traits = range(200) # each cluster is a docvec trait
    db = MongoClient().patents
    mindate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
    maxdate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
    init_pop = load_pop(mindate) # Load the initial population, the patents from the first quarter. 
    return TemporalGPE('tf-idf', 'dna', init_pop)
    #tfidf_gpe_calculators = [TemporalGPE('tf-idf', trait, init_pop) for trait in tfidf_traits]
#    wordvec_gpe_calculators = [TemporalGPE('w2v', trait, init_pop) for trait in docvec_traits]
    

    
    

    

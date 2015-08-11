# Compute the GPE quickly. I.e. not many weeks. 
import numpy as np
import multiprocessing as mp
import cProfile
import csv
import time
import sys
import logging
from datetime import datetime
from pymongo import MongoClient
from alife.util.general import qtr_year_iter, load_obj, dt_as_str, pickle_obj
from alife.util.general import parmap
from alife.traits import _trait_info
from alife.traits.gpe import compute_gpe

# the full path to the directory where the precomputed populations 
# are stored. 
_logfn = 'fast_gpe.log'
_log_format = '%(asctime)s : %(levelname)s : %(message)s'
logging.basicConfig(filename = log_fn, format= log_format, level=logging.INFO)

_pop_dir = '/Users/jmenick/Desktop/alife_refactor/alife/traits/precomputed_pops_qtrs'

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

# helpers
def load_pop(start_date):
    """ Load a list of patents (dictionaries) occuring in the month following the given start_date."""
    filename = '/'.join([_pop_dir, dt_as_str(start_date)+'.p'])
    pop_dict = load_obj(filename)
    assert(start_date == pop_dict['start']) # Make sure the date we think we're loading matches the stored date.
    return pop_dict['descendants']

def running_avg(xsum, N, new_xs):
    """ Update the mean, given new data, if we only know the sum and count of previous data. """
    M = len(new_xs)
    return (xsum + np.sum(new_xs))/float(N+M)
    
def running_cov(N, xsum, ysum, dotxy, new_xs, new_ys, ret_avgs = False):
    """ Update the covariance, given new data and the maintained dot product, sums, and lengths of the two vectors."""
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

def get_rel_num_children(population, rel_avg = True):
    """
    For a given population (here, list of patent documents), 
    return a list (with an element for each member of the population)
    containing how many children each entity has (optionally, relative
    to the average number of children). 
    """
    nchilds = np.array([doc.get('n_citedby', 0) for doc in population])
    if not rel_avg:
        return nchilds
    else:
        avg_childs = np.mean(nchilds)
        return nchilds/float(avg_childs)
    
def get_rel_num_parents(population, rel_avg = True):
    """
    For a given population (here, list of patent documents), 
    return a list (with an element for each member of the population)
    containing how many parents each entity has (optionally, relative
    to the average number of parents). 
    """
    nparents = np.array([doc.get('n_rawcites', 0) for doc in population])
    if not rel_avg:
        return nparents
    else:
        avg_parents = np.mean(nparents)
        return nparents/float(avg_parents)

def get_traits(population, trait_type, trait):
    """
    For a given population, trait type, and trait,
    return an array (with an element for each member of the population)
    whose i^th element indicates the value of the trait in the i^th member
    of the population. This can be binary or real-valued, depending on
    the nature of the trait. The function used to determine the value
    (which can 'binarize') is given in the _trait_info dictionary. 
    """
    _,_,_,trait_val = _trait_info[trait_type]
    return np.array([trait_val(doc, trait) for doc in population])

class TemporalGPE(object):
    """
    A class which computes the GPE for a particular trait over time. 
    """
    def __init__(self, trait_type, trait, anc_pop):
        """
        Initializes a temporal GPE computation with an ancestral population.
        We begin computing the GPE terms upon receiving a descendant population.
        """
        self.i = 0 #counts the number of iterations.
        self.trait_type = trait_type
        self.trait = trait

        self.anc_N = len(anc_pop) # we maintain the size of the ancestral population already processed. 
        _anc_traits = get_traits(anc_pop, self.trait_type, self.trait) 
        _anc_children = get_rel_num_children(anc_pop)
        self.anc_trait_sum = np.sum(_anc_traits) # running sum of the values of ancestor traits.
        self.anc_n_children_sum = np.sum(_anc_children) #running sum of the the cumulative number of ancestors' children.
        self.dot_nc_traits = np.dot(_anc_traits, _anc_children) # running dot product of the trait value vectors and number of children vectors.
        self.prev_t1 = np.cov(_anc_children, _anc_traits)[0][1] # GPE term 1 from the previous timestep. Can be computed before descendant population given.
        self.gpes = [] # A list of four-tuples, the ith of which gives (t1,t2,t3,total) for the ith time step.
        
    def update(self, desc_pop):
        """
        Add a new descendant population - compute the gpe terms for this episode of evolution, 
        and update sufficient statistics for the next episode, adding the descendants into the pool
        of ancestors. 
        """
        desc_M = len(desc_pop)

        # Get the n_children, n_parents, and trait character vectors for the new pop.
        rel_parents = get_rel_num_parents(desc_pop)
        rel_children = get_rel_num_children(desc_pop)
        desc_traits = get_traits(desc_pop, self.trait_type, self.trait)

        # compute GPE terms and maintained quantities
        desc_trait_sum = np.sum(desc_traits)
        desc_trait_avg = float(desc_trait_sum)/desc_M
        anc_trait_avg = self.anc_trait_sum/float(self.anc_N)
        t1 = self.prev_t1
        # np.cov returns a covariance matrix. 
        t3 = np.cov(rel_parents, desc_traits)[0][1]
        gpe_tot = desc_trait_avg - anc_trait_avg
        t2 = gpe_tot + t3 - t1
        self.gpes.append((t1, t2, t3, gpe_tot))
        
        # update prev_t1 and running sums, counts, dot products
        self.prev_t1 = running_cov(self.anc_N, self.anc_n_children_sum, self.anc_trait_sum, self.dot_nc_traits, rel_children, desc_traits)
        self.dot_nc_traits += np.dot(desc_traits, rel_children)
        self.anc_N += desc_M
        self.anc_trait_sum += desc_trait_sum
        self.anc_n_children_sum += np.sum(rel_children)
        self.i += 1

def run_gpe_parmap(db, trait_type, traits, init_year, end_year, init_month=1, end_month=1, debug=True):
    """
    Runs the GPE over time for the given traits and time steps. At each timestep, the traits are updated via a parallel pool map function.
    """
    init_pop = load_pop(datetime(init_year, init_month, 1))
    gpes_list = [TemporalGPE(trait_type, trait, init_pop) for trait in traits]
    current_time = datetime.now()
    for start_year, start_month in qtr_year_iter(init_year, end_year):
        # at each timestep, have threads go after a work queue with gpe updates
        start_date = datetime(start_year, start_month, 1) # The date on which this time step begins.
        logging.info("Updating GPE at time {}".format(start_date))
        logging.info("loading pop...")
        nxt_pop = load_pop(start_date) # nxt_pop holds the descendant population
        logging.info("pop size: {}".format(len(nxt_pop)))
        def mapfunc(gpe_computer):
            logging.info("Updating trait {}...".format(gpe_computer.trait))
            gpe_computer.update(nxt_pop)
            return gpe_computer
        gpes_list = parmap(mapfunc, gpes_list)
        nxt_time = datetime.now()
        logging.info("elapsed: {}".format(nxt_time - current_time))
        current_time = nxt_time
    gpes = {computer.trait: computer.gpes for computer in gpes_list}
    return gpes

def main():
    db = MongoClient().patents
    mindate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
    maxdate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', -1).limit(1))[0]['isd']
    tfidf_traits = _interesting_tfidf_traits + _uninteresting_tfidf_traits
    tfidf_subset = np.random.choice(tfidf_traits, size=10)
    docvec_traits = range(200) # each cluster is a docvec trait
    docvec_subset = np.random.choice(docvec_traits, size=10)
    logging.info("starting with tfidf...")
    gpes_tfidf = run_gpe_parmap(db, 'tf-idf', tfidf_traits,
                                       mindate.year, maxdate.year)
    logging.info("done. pickling...")
    pickle_obj('gpes_tfidf_fast.p', gpes_tfidf)
    logging.info("saving as csv...")
    # Save the computed GPE terms as csvs.
    with open('gpes_tfidf_fast.csv', 'wb') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['trait', 'time_step', 't1', 't2', 't3', 'total'])
        for trait, series in gpes_tfidf.items():
            for step,term_list in enumerate(series):
                writer.writerow([trait, step]+list(term_list))
    logging.info("now for docvec...")
    gpes_docvec = run_gpe_parmap(db, 'w2v', docvec_traits,
                                 mindate.year, maxdate.year)
    logging.info("saving as pickle...")
    # Save the computed GPE terms as python pickles.
    
    pickle_obj('gpes_docvec_fast.p', gpes_docvec)
    
    logging.info("done. saving as csv.")
    with open('gpes_docvec_fast.csv', 'wb') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['trait', 'time_step', 't1', 't2', 't3', 'total'])
        for trait, series in gpes_docvec.items():
            for step,term_list in enumerate(series):
                writer.writerow([trait, step]+list(term_list))
    return gpes_tfidf, gpes_docvec
    
# Test
if __name__ == '__main__':
    logging.info("Getting gpe terms for tfidf and doc2vec...")
    main()
    
        

# Compute the GPE quickly. I.e. not many weeks. 
import numpy as np
import multiprocessing as mp
import cProfile
from datetime import datetime
from pymongo import MongoClient
from alife.util.general import qtr_year_iter, load_obj, dt_as_str
from alife.traits import _trait_info
from alife.traits.gpe import compute_gpe


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

# this should be removed because db assumed. In here now for testing. 
db = MongoClient().patents
mindate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']

# helpers
def load_pop(start_date):
    """ Load a list of patents occuring in the month following the given start_date."""
    filename = '/'.join([_pop_dir, dt_as_str(start_date)+'.p'])
    pop_dict = load_obj(filename)
    assert(start_date == pop_dict['start'])
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
    containing how many children each entity has (optionally, relative)
    to the average number of children. 
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
    containing how many parents each entity has (optionally, relative)
    to the average number of parents. 
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
    whose i^th element indicates whether the i^th member of the population
    has the trait or not. It is binary for now. 
    """
    _,_,_,trait_val = _trait_info[trait_type]
    return np.array([trait_val(doc, trait) for doc in population])

class TemporalGPE(object):
    """
    A class which computes the GPE for a particular trai over time. 
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
        self.prev_t1 = np.cov(_anc_children, _anc_traits)[0][1]
        self.gpes = []
        
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

def run_gpe(db, trait_type, traits, init_year, end_year, init_month=1, end_month=1):
    print "loading init pop..."
    init_pop = load_pop(datetime(init_year, init_month, 1))
    print "initializing GPE..."
    gpes = {trait: TemporalGPE(trait_type,trait, init_pop) for trait in traits}
    current_time = datetime.now()
    for start_year, start_month in qtr_year_iter(init_year, end_year):
        start_date = datetime(start_year, start_month, 1)
        print "Updating GPE at time {}".format(start_date)
        nxt_pop = load_pop(start_date)
        for gpe in gpes.values(): 
            gpe.update(nxt_pop)
        nxt_time = datetime.now()
        print "elapsed: {}".format(nxt_time - current_time)
        current_time = nxt_time
    return gpes

def run_gpe_multithreaded(db, trait_type, traits, init_year, end_year, init_month=1, end_month=1):
    init_pop = load_pop(datetime(init_year, init_month, 1))
    workQueue = mp.Queue()
    returnQueue = mp.Queue()
    for trait in traits:
        workQueue.put(TemporalGPE(trait_type, trait, init_pop))
    returnQueue = mp.Queue()
    for start_year, start_month in qtr_year_iter(init_year, end_year):
        # at each timestep, have threads go after a work queue with gpe updates
        start_date = datetime(start_year, start_month, 1)
        print "Updating GPE at time {}".format(start_date)
        nxt_pop = load_pop(start_date)
        def threadFunc():
            while not workQueue.empty():
                trait_gpe = workQueue.get()
                trait_gpe.update(nxt_pop)
                returnQueue.put(trait_gpe)
        workers = []
        for i in range(mp.cpu_count()):
            p = mp.Process(target=threadFunc)
            p.start()
            workers.append(p)
        for worker in workers:
            worker.join()
        # add the updated gpes for this timestep to the workQueue for the nextstep.
        while not returnQueue.empty():
            workQueue.put(returnQueue.get())
    gpes = {}
    while not workQueue.empty():
        gpe = workQueue.get()
        gpes[gpe.trait] = gpe
    return gpes

def test_run_gpe():
    #Test my GPE implementation against ground truth/previous implementation. Check.

    # load populations for an episode of evolution from disk. 
    ancestors = load_pop(datetime(mindate.year, 1, 1))
    descendants = load_pop(datetime(mindate.year, 4, 1))
    
    # compute new gpe. 
    gpe_new = TemporalGPE('tf-idf', 'structur', ancestors)
    gpe_new.update(descendants)
    new_gpe = gpe_new.gpes[0]

    # compute old gpe. 
    child_char = get_rel_num_children(ancestors)
    par_char = get_rel_num_parents(descendants)
    anc_traits = get_traits(ancestors, 'tf-idf', 'structur')
    desc_traits = get_traits(descendants, 'tf-idf', 'structur')
    old_gpe = compute_gpe(child_char, par_char, anc_traits, desc_traits, sample_cov = True)
    return new_gpe, old_gpe

# Run my new GPE and the old GPE and see how they compare when running over time. 
def new_gpe_benchmarkfn(n_years):
    init_pop = load_pop(datetime(mindate.year, 1, 1))
    gpe = TemporalGPE('tf-idf', 'structur', init_pop)
    current_time = datetime.now()
    for start_year, start_month in qtr_year_iter(mindate.year, mindate.year+n_years):
        nxt_date = datetime(start_year, start_month, 1)
        print "running new GPE at timestep {}".format(nxt_date)
        nxt_pop = load_pop(nxt_date)
        gpe.update(nxt_pop)
        nxt_time = datetime.now()
        print "time elapsed: {}\npop size: {}".format(nxt_time - current_time, len(nxt_pop))
        current_time = nxt_time
    return gpe.gpes
    
def old_gpe_benchmarkfn(n_years):
    init_pop = load_pop(datetime(mindate.year, 1, 1))
    ancestors = init_pop
    gpes = []
    current_time = datetime.now()
    for start_year, start_month in qtr_year_iter(mindate.year, mindate.year+n_years):
        nxt_date = datetime(start_year, start_month, 1)
        print "running old GPE at timestep {}".format(nxt_date)
        nxt_pop = load_pop(nxt_date)
        child_char = get_rel_num_children(ancestors)
        par_char = get_rel_num_parents(nxt_pop)
        anc_traits = get_traits(ancestors, 'tf-idf', 'structur')
        desc_traits = get_traits(nxt_pop, 'tf-idf', 'structur')
        gpes.append(compute_gpe(child_char, par_char, anc_traits, desc_traits))
        ancestors += nxt_pop
        nxt_time = datetime.now()
        print "time elapsed: {}\npop size: {}".format(nxt_time - current_time, len(nxt_pop))
        current_time = nxt_time
    return gpes

def benchmark_fn():
    n_years = 10
    return old_gpe_benchmarkfn(n_years), new_gpe_benchmarkfn(n_years) 

def test(db):
    tfidf_traits = _interesting_tfidf_traits + _uninteresting_tfidf_traits
    docvec_traits = range(200) # each cluster is a docvec trait
    mindate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
    maxdate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', -1).limit(1))[0]['isd']
    gpes = run_gpe(db, 'tf-idf', tfidf_traits, mindate.year, mindate.year+1)
    return gpes

def main():
    db = MongoClient().patents
    tfidf_traits = _interesting_tfidf_traits + _uninteresting_tfidf_traits
    docvec_traits = range(200) # each cluster is a docvec trait
    gpes_tfidf = run_gpe_multithreaded(db, 'tf-idf', tfidf_traits,
                                       mindate.year, mindate.year+2)
    gpes_docvec = run_gpe_multithreaded(db, 'w2v', docvec_traits,
                                       mindate.year, mindate.year+2)

    return gpes_tfidf, gpes_docvec
    
# Test
if __name__ == '__main__':
#    olds, news = benchmark_fn()
#    cProfile.run('benchmark_fn()')
    gpes_tfidf, gpes_docvec = main()
    pickle_obj('gpes_tfidf_fast_test.p', gpes_tfidf)
    pickle_obj('gpes_docvec_fast_test.p', gpes_docvec)


    

    
    

    

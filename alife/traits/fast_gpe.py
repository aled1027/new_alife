"""
Routines for computing the GPE over time, quickly. Does so by iteratively computing covariance.
"""
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
from alife.util.general import parmap, step_thru_qtrs, step_thru_years
from alife.traits import _trait_info
from alife.traits.precompute_pops import get_anc_dec_mark, get_anc_dec_noncum
from alife.traits.determine_traits import almostall, freq_prop_sample, _load_df
from alife.txtmine import stemmer as stemfunc

# the full path to the directory where the precomputed populations
# are stored.
_logfn = 'fast_gpe.log'
_log_format = '%(asctime)s : %(levelname)s : %(message)s'
logging.basicConfig(filename = _logfn, format= _log_format, level=logging.INFO)

_pop_dir = '/Users/jmenick/Desktop/alife_refactor/alife/traits/precomputed_pops_qtrs_fix'

# be sure we are using the right traits.
allstems = [x[0] for x in _load_df()]
_single_tfidf_trait = ['internet']

_interesting_tfidf_traits = ['hyperlink', 'dna', 'internet', 'mobil',
                             'semiconductor', 'softwar', 'batteri', 'crypto',
                             'video', 'fluroesc', 'diode','prosthet',
                             'network', 'cancer', 'neural',
                             'processor', 'smart', 'sequenc', 'jet', 'droplet',
                             'graft', 'link', 'tape', 'film','liquid','ribonucleas', 'gpu', 'gpgpu', 'cpu', 'core', 'intelligen']

_uninteresting_tfidf_traits = ['results','consists','adjustme',
                               'layers','increase','aligned','zone',
                               'include','indicating','applied',
                               'connects','condition','joined','large',
                               'small','path']
tfidf_traits = _interesting_tfidf_traits + _uninteresting_tfidf_traits
_tfidf_traits = [x if x in allstems else stemfunc(x) for x in tfidf_traits]

def get_old_traits():
    """ Grabs terms from original gpe run. Terms are at saved in a numpy 0-d array."""
    file_path = 'data/gpe_terms.npy'
    a = np.load(file_path)
    b = a.item()
    terms = list(b.keys())
    return terms

assert(all(x in allstems for s in _tfidf_traits))

# helpers
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

def load_pop(start_date):
    """ Load a list of patents (dictionaries) occuring in the month following the given start_date."""
    filename = '/'.join([_pop_dir, dt_as_str(start_date)+'.p'])
    pop_dict = load_obj(filename)
    assert(start_date == pop_dict['start']) # Make sure the date we think we're loading matches the stored date.
    return pop_dict['descendants']

def load_anc_dec(start_date, indir):
    """ Load two lists of patents; ancestral and descendant poulation respectively. """
    filename = '/'.join([indir, dt_as_str(start_date)+'.p'])
    pop_dict = load_obj(filename)
    assert(start_date == pop_dict['start']) # Make sure the date we think we're loading matches the stored date.
    return pop_dict['ancestors'], pop_dict['descendants']

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

    e.g. if input=([pat for google, pat for facebook, pat for dry erase board], tf-idf, internet)
         returns np.array([1,1,0]) if google/facebook have internet in tf-idf traits, etc.
    """
    _,_,_,trait_val = _trait_info[trait_type]
    return np.array([trait_val(doc, trait) for doc in population])

class TemporalGPE(object):
    """
    A class which computes the GPE for a particular trait over time.
    It only works if we take the number of children a patent has as fixed :/.
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

class TemporalGPE_NonCum(object):
    """ Compute the gpes over time, when handed a new ancestral population and descendant population at each timestep."""
    def __init__(self, trait_type, trait):
        self.trait_type = trait_type
        self.trait = trait
        self.gpes = []

        # metadata terms
        self.Pa = [] # size of P^a, number of patents with x
        self.Pd = [] # size of P_d
        self.X_bar_a = [] # value of \bar{X^a}
        self.X_bar_d = [] # value of \bar{X_d}
        self.absolute_mutations = [] # \sum_a \sum_d (1 if x^a == x_d else 0)
        # self.quotient = [] # |P^{a_i} \cap P^{a_{i+1}}| / |P^{a_i} \cup P^{a_{i+1}}|

    def data(self):
        return (self.trait_type, self.trait, self.gpes, self.Pa, self.Pd, \
                self.X_bar_a, self.X_bar_d, self.absolute_mutations)

    def update(self, anc_pop, desc_pop):
        """
        Get the statistics we need from the populations to compute the GPE terms.
        anc_pop: list of ancestors, where an element is
        """
        # get_traits returns vector of traits. [0,0,1,0,...] if tf-idf because stemmed.
        anc_traits = get_traits(anc_pop, self.trait_type, self.trait)
        desc_traits = get_traits(desc_pop, self.trait_type, self.trait)
        anc_nchildren = np.array([x.get('n_citedby', 0) for x in anc_pop])
        desc_nparents = np.array([x.get('n_rawcites', 0) for x in desc_pop])
        try:
            nchildren_rel_avg = anc_nchildren/np.mean(anc_nchildren)
        except:
            nchildren_rel_avg = [0 for x in anc_nchildren]
        try:
            nparents_rel_avg = desc_nparents/np.mean(desc_nparents)
        except:
            nparents_rel_avg = [0 for x in desc_nparents]
        gpe_terms = compute_gpe_raw(anc_traits, desc_traits, nchildren_rel_avg, nparents_rel_avg)
        logging.info("trait: {}, gpe_terms: {}".format(self.trait, gpe_terms))
        self.gpes.append(gpe_terms)

        # now update metadata:
        self.Pa.append(np.sum(anc_traits))
        self.Pd.append(np.sum(desc_traits))

        anc_traits = np.array(list(anc_traits))
        desc_traits = np.array(list(desc_traits))
        anc_traits_size = np.size(anc_traits)
        desc_traits_size = np.size(desc_traits)

        self.X_bar_a.append(float(self.Pa[-1]) / float(anc_traits_size))
        self.X_bar_d.append(float(self.Pd[-1]) / float(desc_traits_size))

        max_length = max(anc_traits_size, desc_traits_size)
        anc_traits.resize(max_length)
        desc_traits.resize(max_length)
        self.absolute_mutations.append(np.sum(np.logical_xor(anc_traits, desc_traits)))

        logging.info("trait: {}, Pa: {}, Pd: {}, X_bar_a: {}, X_bar_d: {}, Muts: {}"
                .format(self.trait, self.Pa[-1], self.Pd[-1], self.X_bar_a[-1], self.X_bar_d[-1], self.absolute_mutations[-1]))

def compute_gpe_raw(anc_traits, desc_traits, nchildren_rel_avg, nparents_rel_avg, sample_cov = True):
    """ compute the terms of the gpe for a single trait over a single period of evolution,
    given vectors of ancestor trait values, descendant trait values, ancestor number of children rel. avg
    and descendant number of parents rel avg. By default, use the unbiased sample covariance as an
    estimate of the covariance. If sample_cov is false, use the biased estimator used by excel
    so that it agrees with MAB's excel implementation. The difference is only a factor of (N/N-1). """
    tot = np.mean(desc_traits) - np.mean(anc_traits)
    if sample_cov:
        t1 = np.cov(anc_traits, nchildren_rel_avg)[0][1]
        t3 = np.cov(desc_traits, nparents_rel_avg)[0][1]
    else:
        t1 = _cov2(anc_traits, nchildren_rel_avg)
        t3 = _cov2(desc_traits, nparents_rel_avg)
    t2 = tot + t3 - t1
    return t1,t2,t3,tot

def run_gpe_parmap(db, trait_type, traits, init_year, end_year, init_month=1, end_month=1, debug=True):
    """
    Runs the GPE over time for the given traits and time steps.
    At each timestep, the traits are updated via a parallel pool map function.
    """
    init_pop = load_pop(datetime(init_year, init_month, 1))
    mapfunc1 = lambda x: TemporalGPE(trait_type, x, init_pop)
    gpes_list = parmap(mapfunc1, traits)
    current_time = datetime.now()
    csv_fn = 'alex_output'+'gpes_tfidf.csv'
    with open(csv_fn, 'wb') as outfile:
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

def run_gpe_parmap_noncum(db, trait_type, traits, init_year, end_year, init_month=1, end_month=1, mark=False):
    """
    Runs the GPE over time for the given traits and time steps. At each timestep, the traits are updated via a parallel pool map function.
    """
    mapfunc1 = lambda x: TemporalGPE_NonCum(trait_type, x) # fixes trait_type
    logging.info("Creating TemporalGPE_NonCum Objects")
    gpes_list = parmap(mapfunc1, traits) # generate "TemporalGPE_NonCum" objects for each trait.
    logging.info("Beginning loop over years")

    current_time = datetime.now()
    for (time_0, time_1) in step_thru_years(init_year, end_year, init_month):
        # at each timestep, have threads go after a work queue with gpe updates
        logging.info("Updating GPE at time {}".format(time_0))
        logging.info("loading pops...")
        temptime1 = datetime.now()
        if mark:
            anc_pop, desc_pop = get_anc_dec_mark(db, time_0, time_1, limit = None)
            #anc_pop, desc_pop = load_anc_dec(start_date, indir = _mark_dir)
        else:
            anc_pop, desc_pop = get_anc_noncum(db, time_0, time_1, limit = None)
            #anc_pop, desc_pop = load_anc_dec(start_date, indir = _noncum_dir)
        temptime2 = datetime.now()
        logging.info("time to load pops: {}".format(temptime2 - temptime1))
        logging.info("anc pop size: {}, desc pop size: {}".format(len(anc_pop), len(desc_pop)))
        def mapfunc(gpe_computer):
            logging.info("Updating trait {}...".format(gpe_computer.trait))
            gpe_computer.update(anc_pop, desc_pop)
            return gpe_computer
        gpes_list = parmap(mapfunc, gpes_list)
        nxt_time = datetime.now()
        logging.info("elapsed: {}".format(nxt_time - current_time))
        current_time = nxt_time
    #gpes = {computer.trait: computer.gpes for computer in gpes_list}
    gpes = {trait_object.trait: trait_object.data() for trait_object in gpes_list}
    return gpes

def main_static(name):
    db = MongoClient().patents
    mindate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
    maxdate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', -1).limit(1))[0]['isd']

    tfidf_traits = list(set(freq_prop_sample(3500)+_tfidf_traits))
    docvec_traits = range(200) # each cluster is a docvec trait

    # Runs the GPE calculation for TFIDF
    logging.info("starting with tfidf...")
    gpes_tfidf = run_gpe_parmap(db, 'tf-idf', tfidf_traits,
                                       mindate.year, maxdate.year)

    # Serialize the GPE results as a pickled python dictionary.
    pickle_fn = name+'gpes_tfidf_3k.p'
    logging.info("done. pickling in {}...".format(pickle_fn))
    pickle_obj(pickle_fn, gpes_tfidf)

    # Save the computed GPE terms as csv.
    #csv_fn = name+'gpes_tfidf.csv'
    #logging.info("saving as csv in {}...".format(csv_fn))
    #with open(csv_fn, 'wb') as outfile:
    #    writer = csv.writer(outfile)
    #    writer.writerow(['trait', 'time_step', 't1', 't2', 't3', 'total'])
    #    for trait, series in gpes_tfidf.items():
    #        for step,term_list in enumerate(series):
    #            writer.writerow([trait, step]+list(term_list))

    # Runs the GPE calculation for docvec
    gpes_docvec = None
    #logging.info("now for docvec...")
    #gpes_docvec = run_gpe_parmap(db, 'w2v', docvec_traits,
    #                             mindate.year, maxdate.year)

    ## Serialize the GPE results as a pickled python dictionary.
    #logging.info("saving as pickle...")
    #pickle_obj(name+'gpes_docvec.p', gpes_docvec)

    ## Save the computed GPE terms as csv.
    #logging.info("done. saving as csv.")
    #with open(name+'gpes_docvec.csv', 'wb') as outfile:
    #    writer = csv.writer(outfile)
    #    writer.writerow(['trait', 'time_step', 't1', 't2', 't3', 'total'])
    #    for trait, series in gpes_docvec.items():
    #        for step,term_list in enumerate(series):
    #            writer.writerow([trait, step]+list(term_list))

    return gpes_tfidf, gpes_docvec

def main_noncum(name, mark=False):
    db = MongoClient().patents
    mindate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
    maxdate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', -1).limit(1))[0]['isd']

    #tfidf_traits = list(set(freq_prop_sample(1000)+_tfidf_traits))
    #tfidf_traits = _single_tfidf_trait
    tfidf_traits = list(get_old_traits())
    logging.info("Using {} tfidf traits".format(len(tfidf_traits)))

    # Runs the GPE calculation for TFIDF
    logging.info("starting with tfidf...")
    # TODO undo this for real calculation
    #gpes_tfidf = run_gpe_parmap_noncum(db, 'tf-idf', tfidf_traits, 1980, 1982, mark=mark)
    gpes_tfidf = run_gpe_parmap_noncum(db, 'tf-idf', tfidf_traits, mindate.year, maxdate.year, mark=mark)

    # Serialize the GPE results as a pickled python dictionary.
    pickle_fn = name+'gpes_tfidf_3k.p'
    logging.info("done. pickling in {}...".format(pickle_fn))
    pickle_obj(pickle_fn, gpes_tfidf)

    # Save the computed GPE terms as csv.
    csv_fn = name+'gpes_tfidf_3k.csv'
    logging.info("saving as csv in {}...".format(csv_fn))
    with open(csv_fn, 'wb') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['trait', 'time_step', 't1', 't2', 't3', 'total'])
        for trait, series in gpes_tfidf.items():
            for step,term_list in enumerate(series):
                writer.writerow([trait, step]+list(term_list))

    gpes_docvec = None
    ## Runs the GPE calculation for docvec
    #logging.info("now for docvec...")
    #docvec_traits = range(200) # each cluster is a docvec trait
    #gpes_docvec = run_gpe_parmap_noncum(db, 'w2v', docvec_traits,
    #                             mindate.year, maxdate.year, mark=mark)

    ## Serialize the GPE results as a pickled python dictionary.
    #logging.info("saving as pickle...")
    #pickle_obj(name+'gpes_docvec.p', gpes_docvec)

    ## Save the computed GPE terms as csv.
    #logging.info("done. saving as csv.")
    #with open(name+'gpes_docvec.csv', 'wb') as outfile:
    #    writer = csv.writer(outfile)
    #    writer.writerow(['trait', 'time_step', 't1', 't2', 't3', 'total'])
    #    for trait, series in gpes_docvec.items():
    #        for step,term_list in enumerate(series):
    #            writer.writerow([trait, step]+list(term_list))

    return gpes_tfidf, gpes_docvec

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit("Usage: python {} <'STATIC' or 'NONCUM' or 'MARK'> <NAME>".format(sys.argv[0]))
    name = sys.argv[2]
    if sys.argv[1] == 'STATIC':
        logging.info('running static gpe on patents in {}'.format(_pop_dir))
        main_static(name)
    elif sys.argv[1] == 'NONCUM':
        logging.info('running noncum gpe.')
        main_noncum(name, mark=False)
    elif sys.argv[1] == 'MARK':
        logging.info('running mark style gpe.')
        main_noncum(name, mark=True)
    else:
        sys.exit("Usage: python {} <'STATIC' or 'NONCUM' or 'MARK'> <NAME>".format(sys.argv[0]))




# Determines some traits on which to run GPE as requested by M.A.B. 
from alife.util.general import load_obj
import numpy as np

def _load_df():
    """ Loads a dictionary of document frequencies from disk. Assumes It lives at a particular location on disk. 
    TODO: throw this function (and all such functions) into alife.data
    """
    _data_dir = '/Users/jmenick/Desktop/alife_refactor/output/aggregate_stats'
    _df_fn = '/'.join([_data_dir, 'tfidf_doc_freq.p'])
    try:
        df_dict = load_obj(_df_fn)
    except:
        raise RuntimeError("A document frequency dictionary is not stored in {}.".format(_df_fn))
    return sorted(df_dict.items() ,key = lambda x: x[1])

def middle_of_dist(dfs, low_cutoff_n, high_cutoff_n):
    """ Filters the document frequency list (assumed to be sorted). By keeping the middle of the distribution by rank."""
    return dfs[low_cutoff_n:(-1)*high_cutoff_n]

def middle_of_dist_freq(dfs, low_cutoff_freq, high_cutoff_freq):
    """ Filters the document frequency list (assumed to be sorted). By keeping the middle of the distribution by doc freq cutoff."""
    return [x for x in dfs if low_cutoff_freq < x[1]< high_cutoff_freq]

def freq_prop_sample(n):
    dfs = _load_df()
    subset = [x for x in dfs if 10 < x[1]]
    traits,freqs = zip(*subset)
    probs = map(lambda x: float(x)/np.sum(freqs), freqs)
    return list(np.random.choice(traits, p=probs,size=(n,)))

def almostall():
    dfs = _load_df()
    return [x[0] for x in dfs if 10 < x[1]]

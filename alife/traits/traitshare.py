# subroutines for evaluating the frequency of shared traits among cited and random patents. 
from alife.traits import _trait_info
from alife.util.randpat import PatentSampler
from alife.util.general import pickle_obj
from pymongo import MongoClient
from collections import Counter


def nshared_tfidf(patent1, patent2):
    p1_stems = patent1.get('top_tf-idf', [])
    p2_stems = patent2.get('top_tf-idf', [])
    if p1_stems == [] or p2_stems == []:
        return -1
    else:
        return len(set(p1_stems).and(set(p2_stems)))

def nshared_lda(patent1, patent2):
    p1_topics = patent1.get('top_lda_topic_indices', [])
    p2_topics = patent2.get('top_lda_topic_indices', [])
    if p1_topics == [] or p2_topics == []:
        return -1
    else:
        return len(set(p1_topics).and(set(p2_topics)))

def nshared_w2v(patent1, patent2):
    p1_clusters = patent1.get('top_w2v_cluster_indices', [])
    p2_clusters = patent2.get('top_w2v_cluster_indices', [])
    if p1_clusters == [] or p2_clusters == []:
        return -1
    else:
        return len(set(p1_clusters).and(set(p2_clusters)))

def nshared(patent1, patent2, trait_type):
    nshared_func = nshared_dict[trait_type]
    return nshared_func(patent1, patent2)

def get_cite_pairs(N):
    """ Get a (generator) list (length N) of pairs (x,y) of patents 
    which satisfy the relation 'x cites y'. """
    pass

def get_rand_pairs(N):
    """ Get a (generator) list (length N) of random pairs (x,y) of patents."""
    pass
    
def get_child_parent_set(N):
    """ Get a (generator) list (length N) of two-tuples (child,parents), 
    where parents is a list of patents which are cited by child. """
    pass

def get_parent_child_set(N):
    """ Get a (generator) list (length N) of two-tuples (parent, children) 
    where children is a list of patents which cite parent. """
    pass

def get_child_parset_rand(N):
    """ Get a (generator) list (length N) of two-tuples (child,parents), 
    where parents is a list of patents which are cited by child. """
    pass

def get_par_childset_rand(N):
    """ Get a (generator) list (length N) of two-tuples (parent, children) 
    where children is a list of patents which cite parent. """
    pass


def test():
    db = MongoClient().patents
    all_pairs = db.just_cites.find()
    N = all_pairs.count() 

    # Get counters for each number of shared traits and store as pickled dict. 
    real_shares_pairs = Counter(nshared_tfidf(*p) for p in get_cite_pairs(N))
    pickle_obj('real_shares_counter_pairs.p', dict(real_shares_pairs))
    rand_shares_pairs = Counter(nshared_tfidf(*p) for p in get_rand_pairs(N))
    pickle_obj('rand_shares_counter_pairs.p', dict(rand_shares_pairs))
    real_shares_parset = Counter(nshared_tfidf(*p) for p in get_child_parent_set(N))
    pickle_obj('real_shares_parset.p', dict(real_shares_parset))
    rand_shares_parset = Counter(nshared_tfidf(*p) for p in get_child_parset_rand(N))
    pickle_obj('rand_shares_parset.p', dict(rand_shares_parset))
    real_shares_childset = Counter(nshared_tfidf(*p) for p in get_parent_child_set(N))
    pickle_obj('real_shares_childset.p', dict(real_shares_childset))
    rand_shares_childset = Counter(nshared_tfidf(*p) for p in get_par_childset_rand(N))
    pickle_obj('rand_shares_childset.p', dict(rand_shares_childset))

    
    


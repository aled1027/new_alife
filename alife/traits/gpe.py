# Measure the Generalized Price Equation terms for all of our traits and trait types for arbitrary episodes of evolution.
from alife.util.dbutil import get_fields_unordered as get_fields
from alife.mockdb import get_mock
from alife.traits import _trait_info
from pymongo import MongoClient
import numpy as np

# TODO: get doc vec clusters in db, get lda topics in db. 
def _get_populations(db, time_1, time_2, limit=100, fields = ['top_tf-idf', 'doc_vec', ]):
    """
    Given two times, get an ancestral population, all those occurring before time 1, 
    and a descendant population, all those occuring between time1 and time2.
    This is the crucial function for making sure the analysis is fast. 
    We probably should do something about indexing traits on isd if that won't 
    screw with the memory efficiency. 
    """
    #ancestors = db.patns.find({'isd': {'$lt': time_1}}).limit(limit)
    #descendants = db.patns.find({'isd': {'$gte': time_1, '$lt': time_2}}).limit(limit)
    #return list(ancestors), list(descendants)
    pass

def _get_num_children_char(population, rel_avg = True):
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
    
def _get_rel_num_parents(population, rel_avg = True):
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

def _get_traits(population, trait_type='tf-idf', trait_index=0):
    trait_field, _, densify_func = trait_info[trait_type]
    def trait_val(doc):
        full_vec = densify_func(doc.get(trait_field, []))
        return full_vec[trait_index]
    return [trait_val(doc) for doc in population]

def gpe(db, time_1, time_2, trait_type, trait_index):
    # ancestors, descendants = get_populations(db, time_1, time_2, trait_type)
    # anc_traits, desc_traits = map(lamda x: get_traits(x, trait_type, trait_index), [ancestors, descendants])
    # n_children_rel = _get_rel_num_children(ancestors)
    # n_parents_rel = _get_rel_num_parents(descendants)
    total_diff = np.mean(desc_traits) - np.mean(anc_traits)
    t1 = np.cov(n_children_rel, anc_traits)
    t3 = np.cov(n_parents_rel, desc_traits)
    t2 = total_diff - t1 - t3
    return t1, t2, t3

def main():
    # db = MongoClient().patents
    # trait_type = 'tf-idf'
    # trait_choices = ['internet', 'stuff']
    # time_pairs = get_time_pairs(start_date, end_date, resolution = 'quarter')
    # peq_vals = {trait: [gpe(db, pair[0], pair[1], trait_type, stem2id[trait]) for pair in time_pairs] for trait in trait_choices}
        
        
        
    
    



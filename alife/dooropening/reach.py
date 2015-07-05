# measure 'door-openingness' in patents by a few different ways of measuring reach. 
from pymongo import MongoClient
from itertools import product
from mockdb import get_mock
from alife.util.dbutil import crawl_lineage
from alife.txtmine.w2v import _dist as nrml_cos_sim
from jmAlife.dbManage.parallelMap import partallelMap
import logging

_realdb = MongoClient().patents
_mockdb = get_mock()
_trait_info = {
        'tf-idf': ('top_tf-idf', tfidf_dist),
        'w2v': ('doc_vec', w2v_dist)
    }

def tfidf_dist(traits_a, traits_b):
    """
    measures the 'distance' between two sets of tfidf traits.
    Both are assummed to be lists of strings.
    As these correspond to a dense binary trait vector, the set intersection
    of the two lists is equal to the hamming distance. 
    """
    return 20 - 2*len(list(set(traits_a).intersection(set(traits_b))))

def w2v_dist(traits_a, traits_b):
    """
    The distance between two word2vec vectors is 

    1 - nrml_cos_sim(x,y), 

    where nrml_cos_sim is the cosine similarity of the normalized
    x and y vectors.

    traits_a and traits_b are numpy arrays. 
    """
    traits_a, traits_b = map(np.array, [traits_a, traits_b])
    assert(traits_a.shape[0] == traits_b.shape[0])
    return 1 - nrml_cos_sim(traits_a, traits_b)

""" # JM comment out. Development of this function suspended as it is infeasible. 
def all_pairs_trait_distance(ancestor_pno, trait='w2v', db = _realdb, n_generations = 5):
    #
    #Compute the sum and average pairwise trait distance for all patents in the genealogy descending from the ancestor,
    #up to n_generations down. Measure this for all patent pairs in the lineage regardless of whether or not they 
    #have a citation link. 
    trait_field,dist_func = _trait_info[trait]
    parent = db.traits.find_one({'_id': parent_pno}, {'_id': 1, 'citedby': 1, trait_field:1})
    lineage = crawl_lineage(ancestor_pno, n_generations, fields = ['_id', 'citedby', trait_field], flatten=True,
                            enforce_func = lambda x: True)
    sum_fieldname = 'all_pairs_dist_sum_' + trait
    avg_fieldname = 'all_pairs_dist_avg_' + trait
    stats = {}
    n_with_traits = 0
    dist_sum = 0
    lineage = [doc.get(trait_field, None) for doc in lineage]
"""

def trait_variance(ancestor_pno, trait='w2v', db = _realdb, n_gens = 5):
    """
    Computes the trait mean and variance. 
    """
    stats = {}
    trait_field,dist_func = _trait_info[trait]
    parent = db.traits.find_one({'_id': parent_pno}, {'_id': 1, 'citedby': 1, trait_field:1})
    lineage = crawl_lineage(ancestor_pno, n_gens, fields = ['_id', 'citedby', trait_field], flatten=True,
                            enforce_func = lambda x: True)
    traits = [doc.get(trait_field, None) for doc in lineage]
    traits = np.array([trait for trait in traits if trait is not None])
    mean_field_name = str(n_gens)+'_gen_trait_mean_' + trait
    var_field_name = str(n_gens)+'_gen_trait_variance_' + trait
    stats[mean_field_name] = np.mean(traits, axis=0)
    stats[var_field_name] = np.var(traits, axis=0)
    return stats

def first_order_trait_distance(parent_pno, trait='w2v', db =_realdb):
    """
    Compute the sum and average pairwise trait distance between
    the parent and its children. 
    """
    trait_field,dist_func = _trait_info[trait]
    sum_fieldname = '_'.join(['fotd_sum', trait])
    avg_fieldname = '_'.join(['fotd_avg', trait])
    parent = db.traits.find_one({'_id': parent_pno},{'citedby': 1, trait_field:1})
    stats = {}
    door_openingness = 0
    n_children_with_traits = 0
    if parent[trait_field] is None: #Is None the null value? Or the empty list? 
        logging.warning('No trait field in patent {}.'.format(parent_pno))
        return None # Is this the best null value to return?
    if parent['citedby'] is None:
        stats[sum_fieldname] = 0
        stats[avg_fieldname] = 0
        return stats
    # For each child, measure the distance between its traits and the parent's traits.
    # Keep a running total in door_openingness. 
    for child_pno in parent['citedby']:
        child = db.traits.find_one({'_id': child_pno}, {trait_field:1})
        if child[trait_field] is None:
            logging.warning('No trait field in patent {}.'.format(child_pno))
            continue
        else:
            door_openingness += dist_func(parent[trait_field], child[trait_field])
            n_children_with_traits += 1
    stats[sum_fieldname] = door_openingness
    # The average fotd is the total divided by the number of children (with traits)
    if n_children_with_traits == 0:
        stats[sum_fieldname] = -1
        stats[avg_fieldname] = -1
        return stats
    stats[avg_fieldname] = float(door_openingness)/n_children_with_traits 
    return stats

def compute_tfidf_do():
    def one_tfidf_do(doc):
        return {'$set': first_order_trait_distance(doc['_id'], 'tf-idf')}
    parallelMap(one_tfidf_do,
                in_collection = DB.cite_net,
                out_collection = DB.cite_net,
                findArgs = {
                    'spec': {
                        'top_tf-idf': {'$exists': True},
                        'citedby': {'$exists': True}
                         },
                    'fields':{
                        'top_tf-idf': 1, 'citedby':1, '_id': 1
                    }
                },
                updateFreq = 500,
                bSize = 1000)

def test():
    p = _mockdb.traits.find().next()
    fotd = first_order_trait_distance(p['_id'])
    mv = trait_variance(p['id'])
    return fotd,mv,p

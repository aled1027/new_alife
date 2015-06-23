# measure 'door-openingness' in patents. 
from pymongo import MongoClient
import logging

DB = MongoClient().patents

def tfidf_dist(traits_a, traits_b):
    """
    measures the 'distance' between two sets of tfidf traits.
    Both are assummed to be lists of strings.
    As these correspond to a dense binary trait vector, the set intersection
    of the two lists is equal to the hamming distance. 
    """
    return len(list(set(traits_a)+set(traits_b)))

def first_order_trait_distance(parent_pno, trait='tf-idf'):
    """
    Compute the sum and average pairwise trait distance between
    the parent and its children. 
    """
    trait_info = {'tf-idf': ('tfidfStems', tfidf_dist)} # Later, we will support other traits.
    require(trait=='tf-idf')
    trait_field,dist_func = trait_info[trait]
    parent = DB.cite_net.find_one({'_id': parent_pno},{'citedby': 1, trait_field:1})
    stats = {}
    door_openingness = 0
    n_children_with_traits = 0
    if parent[trait_field] is None: #Is None the null value? Or the empty list? 
        logging.warning('No trait field in patent {}.'.format(parent_pno))
        return None # Is this the best null value to return?
    if parent['citedby'] is None:
        stats['fotd_avg'] = 0
        stats['fotd_sum'] = 0
        return stats
    # For each child, measure the distance between its traits and the parent's traits.
    # Keep a running total in door_openingness. 
    for child_pno in parent['citedby']:
        child = DB.cite_net.find_one({'_id': child_pno}, {trait_field:1})
        if child[trait_field] is None:
            logging.warning('No trait field in patent {}.'.format(child_pno))
            continue
        else:
            door_openingness += dist_func(parent[trait_field], child[trait_field])
            n_childrin_with_traits += 1
    stats['fotd_sum'] = door_openingness
    stats['fotd_avg'] = float(door_openingness)/n_children_with_traits # The average fotd is the total divided by the number of children (with traits)
    return stats
    
    
        
        
    
        
    
    


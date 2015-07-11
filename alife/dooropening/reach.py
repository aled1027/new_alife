# measure 'door-openingness' in patents by a few different ways of measuring reach. 
from pprint import pprint
from pymongo import MongoClient
from alife.mockdb import get_mock
from alife.util.dbutil import crawl_lineage
from jmAlife.dbManage.parallelMap import parallelMap
from alife.traits import _trait_info
import logging
import numpy as np

# Below is a dictionary keyed by trait name, which contains a tuple of the field name in the db, the distance function, and the densify function.

def trait_variance(ancestor_pno, db, trait='w2v', n_gens = 2, enforce_func = lambda x: True):
    """
    Computes the trait mean and variance*. For now the variance is the norm of the vector of component-wise variances.  
    """
    # TODO: Need to unfold tfidfs into sparse vector to compute variance. 
    if trait == 'lda':
        raise RuntimeError('Trait variance not currently supported for {}'.format(trait))
    stats = {}
    mean_field_name = str(n_gens)+'_gen_trait_mean_' + trait
    var_field_name = str(n_gens)+'_gen_trait_variance_' + trait
    trait_field, _, densify_func = _trait_info[trait]
    parent = db.traits.find_one({'_id': ancestor_pno}, {'_id': 1, 'citedby': 1, trait_field:1})
    lineage = crawl_lineage(db, ancestor_pno, n_gens, fields = ['_id', 'citedby', trait_field], flatten=True, enforce_func = enforce_func)
    if lineage is None: 
        stats[mean_field_name] = -1
        stats[var_field_name] = -1
        return stats
    traits = [doc.get(trait_field, None) for doc in lineage]
    traits = np.array([densify_func(t) for t in traits if t is not None], dtype=np.float64)
    if len(traits) > 1:
        stats[mean_field_name] = list(np.mean(traits, axis=0))
    elif len(traits) == 1:
        stats[mean_field_name] = traits
    elif len(traits) == 0:
        stats[mean_field_name] = -1
        stats[var_field_name] = -1
        return stats
    else:
        raise RuntimeError("Less than 0 traits???")
    stats[var_field_name] = np.linalg.norm(np.var(traits, axis=0)) # For now, get a real number by computing norm. 
    return stats

def parent_child_trait_distance(ancestor_pno, db, trait='w2v', n_gens = 2, enforce_func = lambda x: True):
    """
    Computes the sum and average of the parent-descendant trait distances for every descendant begot by the patent
    with pno given by the 'ancestor_pno' argument. The appropriate distance function
    for the given trait is looked up in the _trait_info dictionary. The distance function is then evaluated
    for each descendent in the lineage from the ancestor, up to n_gens in the future. The returned 
    dictionary contains the sum and average fields, with both fields equal to zero if the patent in question has no
    children, and set to -1 as a kind of error value, if none of its descendants have traits. The argument 'enforce_func'
    allows the user to set a condition which must be met in order for a patent to be included in the lineage. For instance,
    the enforce_func, 

        lambda x: len(x.get('citedby', [])) > 100
    
    Would enforce that patents only be included in the lineage if they have more than 100 incoming citations.
    """
    if trait == 'lda':
        raise RuntimeError('Trait variance not currently supported for {}'.format(trait))
    stats = {}
    sum_fieldname = '_'.join([str(n_gens), 'gen_sum_dist', trait])
    avg_fieldname = '_'.join([str(n_gens), 'gen_avg_dist', trait])
    trait_field,dist_func, _ = _trait_info[trait]
    parent = db.traits.find_one({'_id': ancestor_pno}, {'_id': 1, 'citedby': 1, trait_field:1})
    if parent is None:
        return None # We don't have that ancestor. 
    lineage = crawl_lineage(db, ancestor_pno, n_gens, fields = ['_id', 'citedby', trait_field], flatten=True, enforce_func = enforce_func)[1:]
    if lineage is None:
        stats[sum_fieldname] = -1
        stats[avg_fieldname] = -1
        return stats
    if not (parent.get('citedby', None) and parent.get(trait_field, None)):
        stats[sum_fieldname] = 0
        stats[avg_fieldname] = 0
        return stats
    traits = [doc.get(trait_field, None) for doc in lineage]
    traits = np.array([t for t in traits if t is not None], dtype=np.float64)
    n_children_with_traits = len(traits)
    if n_children_with_traits == 0:
        stats[sum_fieldname] = -1
        stats[avg_fieldname] = -1
        return stats
    dist_sum = np.sum([dist_func(parent.get(trait_field), trait) for trait in traits])
    stats[sum_fieldname] = dist_sum
    stats[avg_fieldname] = dist_sum/n_children_with_traits
    return stats

def compute_reach(db, trait='w2v', n_gens=2, family=None, enforce_func = lambda x: True):
    trait_field, _, _ = _trait_info[trait]
    def one_reach(doc):
        return {'$set': parent_child_trait_distance(doc['_id'], n_gens=n_gens, trait=trait, db=db, enforce_func = enforce_func)}
    if family is not None:
        for doc in family:
            logging.info("Computing {} gen {} reach for patent {}".format(n_gens, trait, doc['_id']))
            db.traits.update({'_id': doc['_id']}, one_reach(doc))
    else:
        parallelMap(
            one_reach,
            in_collection = db.traits,
            out_collection = db.traits,
            findArgs = {
                'spec': {trait_field: {'$exists': True}},
                'fields': {trait_field: 1, 'citedby': 1, '_id': 1}
            },
            updateFreq=500,
            bSize = 1000
        )

def compute_trait_variance(db, trait='w2v', n_gens=2, family=None, enforce_func = lambda x: True):
    trait_field, _, _ = _trait_info[trait]
    def one_trait_var(doc):
        return {'$set': trait_variance(doc['_id'], n_gens=n_gens, trait = trait, db=db, enforce_func = enforce_func)}
    if family is not None:
       for doc in family:
           logging.info("Computing {} gen {} trait variance for patent {}".format(n_gens, trait, doc['_id']))
           db.traits.update({'_id': doc['_id']}, one_trait_var(doc))
    else:
        parallelMap(
            one_trait_var,
            in_collection = db.traits,
            out_collection = db.traits,
            findArgs = {
                'spec': {trait_field: {'$exists': True}},
                'fields': {trait_field: 1, 'citedby': 1, '_id': 1}
            },
            updateFreq=500,
            bSize = 1000
        )

def test():
    enforce_func = lambda x: len(x.get('citedby', [])) > 100
    realdb = MongoClient().patents
    patent_family = [4061724, 4064521, 4340563, 4405829, 4655771, 4683202, 4723129, 5103459, 5143854, 5572643]
    print "Getting docs from real db..."
    patent_family_docs = [realdb.traits.find_one({'_id': pno}) for pno in patent_family]
#    pprint(patent_family_docs)
    mockdb = get_mock()
    print "computing 2 generation tf-idf reach..."
    compute_reach(trait='tf-idf', n_gens=2, db=mockdb, family=patent_family_docs, enforce_func = enforce_func)
    print "computing 2 generation w2v reach..."
    compute_reach(trait='w2v', n_gens=2, db=mockdb, family=patent_family_docs, enforce_func = enforce_func)
    print "computing 2 generation w2v trait variance..."
    compute_trait_variance(trait='w2v', n_gens=2, db=mockdb, family=patent_family_docs, enforce_func = enforce_func)
    print "computing 5 generation tf-idf reach..."
    compute_reach(trait='tf-idf', n_gens=5, db=mockdb, family=patent_family_docs, enforce_func = enforce_func)
    print "computing 5 generation w2v reach..."
    compute_reach(trait='w2v', n_gens=5, db=mockdb, family=patent_family_docs, enforce_func = enforce_func)
    print "computing 5 generation w2v trait variance..."
    compute_trait_variance(trait='w2v', n_gens=5, db=mockdb, family=patent_family_docs, enforce_func = enforce_func)
    print "Done testing."

def main(db, family=None):
    compute_reach(trait='w2v', n_gens=5, db=db, family=family)

if __name__ == '__main__':
    realdb = MongoClient().patents
    patent_family = [4061724, 4064521, 4340563, 4405829, 4655771, 4683202, 4723129, 5103459, 5143854, 5572643]
    patent_family_docs = [realdb.traits.find_one({'_id': pno}) for pno in patent_family]
    main(realdb, patent_family_docs)

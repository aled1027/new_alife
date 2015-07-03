# Utilities for reading data from mongodb. 
from collections import defaultdict
from pymongo import MongoClient
from alife import mockdb
from alife.util.general import save_dict

_db = MongoClient().patents

def get_texts(patents, coll_name = 'pat_text', generator = False):
    """
    Access the text field from an iterable of patent documents.
    The iterale can be a database cursor, a mock database cursor, 
    a list, a generator, etc, so long as hit holds dictionaries. 
    """
    require(coll_name in ['pat_text, patns'])
    if coll_name == 'pat_text':
        texts = (pat['patText'] for pat in patents)
    elif coll_name == 'patns':
        texts = (pat['title'] + ' ' + pat['abstract'] for pat in patents)
    else:
        raise RuntimeError('Collection {} not supported, or has no text field'.format(coll_name))
    if generator:
        return texts
    else:
        return list(texts)

def crawl_lineage(ancestor_pno, n_generations=3,fields = ['_id', 'citedby'], 
                  enforce_func = lambda pat: len(pat.get('citedby', [])) > 75, 
                  flatten = False, collection = _db.traits):
    """
    Get all patents children of ancestor_pno, and children's children..., 
    and so on, with n_generations total generations of patents. 
    Returns a list of lists of patent documents, where each inner list
    contains all patents in a given generation satisfying enforce_func. 
    """
    ancestor_doc = collection.find_one({'_id': ancestor_pno}, {field:1 for field in fields})
    lineage = [[ancestor_doc]]
    for i in range(1,n_generations):
        ancestors = [pat for pat in lineage[i-1]]
        descendants = []
        for a in ancestors:
            for child_pno in a['citedby']:
                child_doc = collection.find_one({'_id': int(child_pno)}, {field: 1 for field in fields})
                if child_doc is None:
                    continue
                else:
                    # begin jm clooj. 
                    if enforce_func(child_doc):
                        descendants.append(child_doc)
        if descendants is None:
            return lineage
        lineage.append(list(set(descendants))) # get the unique ones only
    if flatten:
        lineage = [pat for subnet in lineage for pat in subnet]
    return lineage

def subnet_adj_dict(patents):
    """
    forms a sparse adjacency dictionary from an iterable of patents. 
    this is not efficient code - it should only be done for reasonably sized lists. 
    """
    pnos = [patent['_id'] for patent in patents]
    incites = {pno: [] for pno in pnos}
    for patent in patents:
        citee_pno = patent['_id']
        for citer_pno in patent.get('citedby', None):
            if citer_pno in pnos:
                incites[citee_pno].append(int(citer_pno))
    return incites

def test():
    pass

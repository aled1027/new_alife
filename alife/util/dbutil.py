# Utilities for reading data from mongodb. 

# TODO - in the testing environment, need to find a way to share the collection accross processes. 

import random
import logging
import multiprocessing as mp
from collections import defaultdict
import pymongo
import mongomock as mm
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from alife import mockdb
from alife.util.general import save_dict
import numpy as np

"""
def get_texts(patents, coll_name = 'pat_text', generator = False):
   #    Access the text field from an iterable of patent documents.
#    The iterale can be a database cursor, a mock database cursor, 
#    a list, a generator, etc, so long as hit holds dictionaries. 
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
"""

def get_fields_unordered(collection, field_names=None, null_values=None, limit = None):
    """
    Returns an nd-array, one for each element of the collection,
    or limited to a certain number of rows. The columns are the fields.
    If we don't have a field instead return the specified null value. 
    """
    projection = {}
    if null_values is None:
        null_values = [None for _ in field_names]
    projection = {field:1 for field in field_names}
    if limit:
        data = collection.find({},projection).limit(limit)
    else:
        data = collection.find({},projection)
    outarr = []
    for pat in data:
        row = [pat.get(field, nil) for field,nil in zip(field_names, null_values)]
        outarr.append(row)
    return np.array(outarr).transpose()

def get_field_generator(collection, field_name, null_value=None, limit = None):
    """
    Returns an nd-array, one for each element of the collection,
    or limited to a certain number of rows. The columns are the fields.
    If we don't have a field instead return the specified null value. 
    """
    projection = {}
    projection = {field_name:1}
    if limit:
        data = collection.find({},projection).limit(limit)
    else:
        data = collection.find({},projection)
    return (x for x in (pat.get(field_name, null_value) for pat in data) if x is not null_value)

def crawl_lineage(db, ancestor_pno, n_generations=3,fields = ['_id', 'citedby'], 
                  enforce_func = lambda pat: len(pat.get('citedby', [])) > 75, 
                  flatten = False):
    """
    Get all patents children of ancestor_pno, and children's children..., 
    and so on, with n_generations total generations of patents. 
    Returns a list of lists of patent documents, where each inner list
    contains all patents in a given generation satisfying enforce_func. 
    """
    ancestor_doc = db.traits.find_one({'_id': ancestor_pno}, {field:1 for field in fields})
    if ancestor_doc is None:
        return None
    lineage = [[ancestor_doc]]
    for i in range(1,n_generations):
        ancestors = [pat for pat in lineage[i-1]]
        descendants = []
        for a in ancestors:
            for child_pno in a.get('citedby', []):
                child_doc = db.traits.find_one({'_id': int(child_pno)}, {field: 1 for field in fields})
                if child_doc is None:
                    continue
                else:
                    # begin jm clooj. 
                    if enforce_func(child_doc) and not any(d['_id']==child_doc['_id'] for d in descendants):
                        descendants.append(child_doc)
        if descendants is None:
            return lineage
        lineage.append(descendants)
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
        for citer_pno in patent.get('citedby', []):
            if citer_pno in pnos and citer_pno not in incites[citee_pno]:
                incites[citee_pno].append(int(citer_pno))
    return incites


def parallelMap(func, collection, id_field_name, enforce_func = None,
                updateFreq=50, verbose=True):
                """
                Refactored Drew Blount's Parallel map to make it testable in a mockdb environment.
                This takes as input a function and collection, and maps the function
                over the whole collection. It is intended for particular kinds of functions:
                those which update a field or set of fields for a single document. 
                So func is required to take as input a single document and 
                return a dictionary which may be passed as the argument to a batch.update() method.
                E.g of the form 
                
                    {'$set': {'my_field1': my_value, 'myfield2': value}}
                
                
                The findArgs parameter allows the user to subset the collection by only 
                mapping the function over documents which match a query given in findArgs[spec]. 
                findArgs[fields] is a projection, determining which fields are in play for the function.

                the updateFreq parameter determines how often the bulk operation is executed. 

                This version of the code does not bother with cursor batches. It will be interesting 
                to see a benchmark.
                """
                if enforce_func is None:
                    enforce_func = lambda x: True

                def partFunc(cursor, collection):
                    if type(collection) == pymongo.collection.Collection:
                        """
                        If the collection is a real pymongo collection,
                        operate as usual with bulk ops. 
                        """
                        bulk = collection.initialize_unordered_bulk_op()
                        updateNum = 0
                        anyToAdd = False
                        for doc in cursor:
                            if not enforce_func(doc):
                                continue
                            updateNum += 1
                            out = func(doc)
                            if out:
                                bulk.find({id_field_name: doc[id_field_name]}).update_one(out)
                                anyToAdd = True
                            if updateNum == updateFreq:
                                if anyToAdd:
                                    bulk.execute()
                                    bulk = collection.initialize_unordered_bulk_op()
                                    anyToAdd = False
                                updateNum = 0
                        if anyToAdd:
                            bulk.execute()
                    elif type(collection) == mm.collection.Collection:
                        for doc in cursor:
                            if not enforce_func(doc):
                                continue
                            if verbose == True:
                                print "enforce func holds for patent {}".format(doc[id_field_name])
                            res = collection.update({id_field_name: doc[id_field_name]},func(doc))
                            if verbose:
                                print res
                    else:
                        raise RuntimeError("collection type is not pymongo or mongomock??")

                cursors = collection.parallel_scan(mp.cpu_count())
                workerProcesses = []
                for c in cursors:
                    p = mp.Process(target=partFunc, args=(c,))
                    p.daemon = True
                    p.start()
                    workerProcesses.append(p)
                    p.join()

                for p in workerProcesses:
                    p.join()

                return collection.find({'dummy_field': 'yay!'}).count()
    
def test():
    patns = mockdb.get_mock().patns
    def test_func(doc):
        return {'$set': {'dummy_field': 'yay!'}}
    n_right = parallelMap(test_func, patns, 'pno')
    print "num for which alleged successfull: {}".format(n_right)
    print "num with dummy_field: {}".format(patns.find({'dummy_field': 'yay!'}).count())
    return patns


# Inserts a field for every document containing their cluster strengths (in decreasing order of similarity). 

from pymongo import MongoClient
from alife.util import model_loader
from alife.txtmine.w2v import cluster_distances
from jmAlife.dbManage.parallelMap import parallelMap
from pprint import pprint

def test(n_docs = 100):
    db = MongoClient().patents
    w2v,kmeans = model_loader(300,200)
    def part_func(doc):
        return {'$set': {'wordvec_clusters': cluster_distances(db, doc['_id'], w2v,kmeans)}}
    for doc in db.traits.find({'doc_vec': {'$exists': True, '$nin': [[0 for _ in range(300)]]}, 'top_tf-idf': {'$nin': [[]]}}).limit(n_docs):
        pprint(part_func(doc))
#        db.traits.update({'_id': doc['_id']}, part_func(doc))
#    return db

def main():
    db = MongoClient().patents
    w2v,kmeans = model_loader(300,200)
    def part_func(doc):
        return {'$set': {'wordvec_clusters': cluster_distances(db, doc['_id'], w2v,kmeans)}}
    parallelMap(
        part_func,
        in_collection = db.traits,
        out_collection = db.traits,
        findArgs = {
            'spec': {'doc_vec': {'$exists': True, '$nin': [[0 for _ in range(300)]]}, 'top_tf-idf': {'$nin': [[]]}},
            'fields': {'_id': 1}
        },
        updateFreq=500,
        bSize=1000
    )
    
if __name__ == '__main__':
    main()

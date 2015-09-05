# Inserts a field for every document containing their cluster strengths (in decreasing order of similarity). 

import sys
from pymongo import MongoClient
from alife.util import model_loader
from alife.txtmine.w2v import cluster_distances
from jmAlife.dbManage.parallelMap import parallelMap
from pprint import pprint

def test(n_docs = 100):
    db = MongoClient().patents
    w2v,kmeans = model_loader(300,200)
    def part_func(doc):
        try:
            return {'$set': {'wordvec_clusters': cluster_distances(db, doc['_id'], w2v,kmeans)}}
        except:
            return {'$set': {'wordvec_clusters': []}}
    for doc in db.traits.find().limit(n_docs):
        pprint(part_func(doc))

def main():
    db = MongoClient().patents
    w2v,kmeans = model_loader(300,200)
    def part_func(doc):
        try:
            return {'$set': {'wordvec_clusters': cluster_distances(db, doc['_id'], w2v,kmeans)}}
        except:
            return {'$set': {'wordvec_clusters': []}}
    parallelMap(
        part_func,
        in_collection = db.traits,
        out_collection = db.traits,
        findArgs = {
            'spec': {}, 'fields': {}
        },
        updateFreq=500,
        bSize=1000
    )
    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        exit("Usage: {} <'test' or 'run'>")
    if sys.argv[1] == 'test':
        test()
    elif sys.argv[1]  == 'run':
        main()
    else:
        exit("Usage: {} <'test' or 'run'>")


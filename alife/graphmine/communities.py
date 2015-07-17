# detect communities in patents genealogies 
from alife.util.dbutil import crawl_lineage, subnet_adj_dict
from alife.mockdb import get_mock
from community import detect, visualize, util

from pymongo import MongoClient

def test():
    db = MongoClient().patents
    pno = 6000704
    lineage = crawl_lineage(
        db, pno, n_generations = 3, 
        enforce_func = lambda x: True,
        flatten=True
    )
    adj = subnet_adj_dict(lineage)
    detector = detect.CommunityDetector(adj)
    communities = detector.run()
    community_lookup = util.get_community_lookup(communities)
    return community_lookup

def main():
    pass

if __name__ == '__main__':
    test()
    
    


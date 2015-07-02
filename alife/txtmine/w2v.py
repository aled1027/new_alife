# utilities for fitting and analysing word2vec-based trait models. 
import numpy as np
from collections import defaultdict
from pymongo import MongoClient
from gensim import models
from gensim import matutils
from sklearn.externals import joblib
from alife.mockdb import get_mock
from alife.txtmine import stemmer
from alife.util import model_loader
from alife.util.general import cosine_dist, euclidean_dist, save_dict
from alife.txtmine.tokenizer import Tokenizer
from alife.visualize.w2v_vis import embedding_fig
from pprint import pprint

_db = MongoClient().patents
_tokenizer = Tokenizer()
_friendly_patents = [('zeolites', 4061724), ('semiconductors', 4064521), 
                        ('nonwoven webs', 4340563), ('rsa', 4405829), 
                        ('stents', 4655771), ('pcr', 4683202),
                        ('bubble jet', 4723129), ('cell phone', 5103459),
                        ('microarrays', 5143854), ('browser', 5572643)]
_names,_pnos = zip(*_friendly_patents)

def _dist(v1,v2):
    return np.dot(matutils.unitvec(v1), matutils.unitvec(v2))

def load_w2v(filename):
    #Loads a word2vec model stored at the given location.
    return models.word2vec.Word2Vec.load(filename)

def load_kmeans(filename):
    # Loads a kmeans model stored at the given location.
    return joblib.load(filename)

def parse_clusters(kmeans, w2v, n_get = 50, n_try = 20, stemmeq=True):
    """
    parses a kmeans model by returning the closest word vectors. 
    if stemmeq is True, then keep searching through the closest
    words until you get up to n_try which do not have the same stem.
    """ 
    centers = kmeans.cluster_centers_
    if not stemmeq:
        parsed = {i:','.join(
            map(lambda x: x[0], w2v.most_similar([center], topn=n_try))
        ) 
                  for i,center in enumerate(centers)}
    else:
        parsed = defaultdict()
        for i,center in enumerate(centers):
            terms = []
            topn_get = w2v.most_similar([center], topn = n_get)
            for term in topn_get:
                if len(terms) == n_try:
                    break
                if stemmer(term[0]) not in [stemmer(t) for t in terms]:
                    terms.append(term[0])
                else:
                   continue 
            parsed[i] = terms
    return parsed

def tfidf_weighted_avg(pno, w2v_model):
    """
    computes the tfidf-weighted average representation of a doc 
    in a given word2vec model.
    This is poorly implemented in that it makes two database queries. Ugh. 
    """
    text = _db.pat_text.find_one({'_id': pno}).get('patText', '')
    words = _tokenizer.tokenize(text)    
    stemmed_words = [stemmer(word) for word in words]
    bow = _db.patns.find_one({'pno': pno}).get('text')
    tfidfs = [bow.get(stem,{}).get('tf-idf',0) for stem in stemmed_words]
    def getvec(word,model):
        try:
            return model[word]
        except:
            return np.zeros(len(model['dna']))
    vecs = [getvec(word,w2v_model) for word in words]
    weighted_vecs = np.array([vec*tfidf for (vec,tfidf) in zip(vecs,tfidfs)])
    assert(len(tfidfs) == len(words) == len(stemmed_words) == len(vecs) == len(weighted_vecs))
    return 1./len(words)*np.sum(weighted_vecs, axis=0)

def distances_from(v1, other_vs):
    """
    Returns a list of distances from v1 to each vector in other_vs.
    If cosine is true, use the cosine distance rather than the 
    euclidean distance.     
    """
    
    return [_dist(v1,v2) for v2 in other_vs]
#    if cosine:
#        return [cosine_dist(v1,v2) for v2 in other_vs]
#    else:
#        return [euclidean_dist(v1,v2) for v2 in other_vs]
    
    
def cluster_distances(pno, w2v_model, cluster_model, srtd = True):
    """
    Returns a list of distances between the vector representing the
    patent with the given number in the w2v_model and each of the 
    cluster centers in the cluster_model. 
    """
    vec_representation = tfidf_weighted_avg(pno, w2v_model)
    dists =  distances_from(vec_representation, cluster_model.cluster_centers_)
    if srtd:
        return sorted(enumerate(dists), key = lambda x: x[1], reverse=True)
    else:
        return dists

def model_report(pnos, w2v_model, cluster_model, outdir, top_n=10):
    """
    Summarize the trait assigned to the document by the models. 
    Do so by returning the parse for the top_n clusters by strength
    """
    parsed_clusters = parse_clusters(cluster_model, w2v_model)
    dists = {name: cluster_distances(pno, w2v_model, cluster_model)
             for name,pno in pnos}
    cluster_parse_fn = '/'.join([outdir, 'parsed_clusters.p'])
    dist_fn = '/'.join([outdir, 'patent_dists.p'])
    tsne_fn = '/'.join([outdir, 'embedding_fig_tsne.png'])
    save_dict(cluster_parse_fn, parsed_clusters)
    save_dict(dist_fn, dists)
    embedding_fig(w2v_model, cluster_model, savefn = tsne_fn, n=300)

def test():
    w2v,kmeans = model_loader(300,200)
    dists = {name: cluster_distances(pno, w2v,kmeans)
             for (name,pno) in _friendly_patents
    }
    return w2v, kmeans, dists, parse_clusters(kmeans, w2v)


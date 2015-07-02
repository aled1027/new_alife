# temporary code for model eval. 
from sklearn.externals import joblib
from gensim import models

_model_dir = '/Users/jmenick/Desktop/jmAlife/output/models'
def _fn(name): return '/'.join([_model_dir, name])
_w2v_locs = {
    50:_fn('w2v_50vs_50nc/w2v50.word2vec'), 
    100: _fn('w2v_100vs_100nc/w2v100.word2vec'), 
    300: _fn('w2v_300vs_200nc/w2v300.word2vec')
}
_cluster_locs = {
    (50,50): _fn('w2v_50vs_50nc/kmeans50.pkl'), 
    (50,100): _fn('w2v_50vs_100nc/kmeans100'), 
    (50,200): _fn('w2v_50vs_200nc/kmeans200'), 
    (50,300): _fn('w2v_50vs_300nc/kmeans300'),
    (100,50): _fn('w2v_100vs_50nc/kmeans50'), 
    (100,100): _fn('w2v_100vs_100nc/kmeans100.pkl'),
    (100,200): _fn('w2v_100vs_200nc/kmeans200'), 
    (100,300): _fn('w2v_100vs_300nc/kmeans300'),
    (300, 50): _fn('w2v_300vs_50nc/kmeans50'), 
    (300,100): _fn('w2v_300vs_100nc/kmeans100'), 
    (300,200): _fn('w2v_300vs_200nc/kmeans200.pkl'), 
    (300,300): _fn('w2v_100vs_300nc/kmeans300')
}

def model_loader(vec_size=300, n_clusters=300):
    try:
        w2v_fn = _w2v_locs[vec_size]
    except:
        raise RuntimeError('Word2vec model with vector size {} not found.'.format(vec_size))
    try:
        kmeans_fn = _cluster_locs[(vec_size,n_clusters)]
    except: 
        raise RuntimeError('Kmeans model with vec size {} and {} clusters not fond.'.format(vec_size, n_clusters))
    w2v = models.word2vec.Word2Vec.load(w2v_fn)
    kmeans = joblib.load(kmeans_fn)
    return w2v,kmeans
    

from alife.data import load_file
from alife.txtmine.w2v import _dist as nrml_cos_sim

_stem2id = load_file('stem2id')

def densify_tfidf(top_tfidf):
    """ convert a 'top_tfidf' list of stems into a dense trait vector. """
    n_stems = len(_stem2id)
    dense_vec = [0 for _ in range(n_stems)]
    for stem in top_tfidf:
        dense_vec[word2id[stem]] = 1
    return np.array(dense_vec)

def densify_lda(topic_strengths, K=200, normalize=True):
    """
    Given a list of tuples [(topic, strength), ...] and the number of topics
    in the LDA model, get a full dense trait vector [s_1, s_2, ..., s_K].
    If normalize is true, set the zeroes to some small number so that the vector sums to 1. 
    """
    if not normalize:
        strengths = [0 for _ in range(K)]
        for topic,strength in topic_strengths:
            strengths[topic] = strength
    else:
        n_traits = 0
        tot = 0
        for topic,strength in topic_strengths:
            n_traits += 1
            tot += strength
        zero_val = (1-tot)/float(K-n_traits)
        strengths = [zero_val for _ in range(K)]
        for topic,strength in topic_strengths:
            strengths[topic] = strength
    return np.array(strengths)

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

def lda_dist(traits_a, traits_b):
    """
    Take the cosine distance between topic mixture vectors. 
    """
    traits_a, traits_b = map(densify_lda, [traits_a, traits_b])
    assert(traits_a.shape[0] == traits_b.shape[0])
    return 1 - nrml_cos_sim(traits_a, traits_b)

_trait_info = {
        'tf-idf': ('top_tf-idf', tfidf_dist, densify_tfidf),
        'w2v': ('doc_vec', w2v_dist, lambda x: x),
        'lda': ('lda_topics', lda_dist, densify_lda)
}

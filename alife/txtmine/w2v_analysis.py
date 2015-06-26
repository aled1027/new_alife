# Analyse models. 

def tfidf_weighted_avg(pno, w2v_model):
    """
    computes the tfidf-weighted average representation of a doc 
    in a given word2vec model.
    """
    # words = get_words(pno)
    # stemmed = [stemmer(word) for word in words]
    # tfidfs = [doc.tfidf[word] for word in stemmed]
    # vecs = [w2v.get_vec(word) for word in words]
    # return (1/len(words))*sum([vec*tfidf for (vec,tfidf) in zip(vecs,tfidfs)])
    pass

def distances_from(v1, other_vs):
    """
    Returns a list of distances from v1 to each vector in other_vs
    """
    pass
    
def cluster_distances(pno, w2v_model, cluster_model):
    """
    Computes the cluster distances from the doc representation
    """
    # vec_representation = tfidf_weighted_avg(pno, w2v_model)
    # return distances_from(vec_representation, cluster_model.centers)
    pass

def model_report(pno, w2v_model, cluster_model, top_n=10):
    """
    Summarize the trait assigned to the document by the models. 
    Do so by returning the parse for the top_n clusters by strength
    """
    # distances = cluster_distances(pno, w2v_model, cluster_model)
    # parsed_clusters = parse_clusters(cluster_model, w2v_model)
    # sorted_clusters = [x[0] for x in sorted(enumerate(cluster_distances), key = lambda x: x[1])]
    # return [parsed_clusters[i] for i in sorted_clusters[top_n]]
    
if __name__ == '__main__':
    # allstar_pnos = [a,b,c,...,d]
    # reports = {pno: model_report(pno, w2v_model, cluster_model,10) for pno in allstar_pnos}
    # write reports to csv. 
    pass
    

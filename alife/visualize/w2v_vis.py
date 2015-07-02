# utilities for visualizing word2vec clusters. 
import numpy as np
import matplotlib.pyplot as plt
from sklearn.externals import joblib
from sklearn.decomposition import PCA
from tsne import bh_sne
from gensim import models,corpora
from alife.visualize.discrete_color import discrete_color_scheme 

def embedding_fig(w2v_model, kmeans_model, n=500, embed_style = 'tsne', savefn = None, show=False):
    """
    Save or show a matplotlib figure, displaying word embeddings colored
    according to cluster assignment. The parameter n gives the number of 
    words to show, in decreasing order of frequency in the dataset. 

    """
    freqs = {x: y.count for x,y in w2v_model.vocab.items()}
    words,word_vecs = w2v_model.index2word, w2v_model.syn0
    srtd_indices, srtd_words = zip(*sorted(list(enumerate(words)), key = lambda x: freqs[x[1]], reverse=True))
    srtd_vecs = np.array([word_vecs[i] for i in srtd_indices])
    subset_words, subset_vecs = srtd_words[:n], srtd_vecs[:n]
    # map cluster assignment to integer.
    subset_clusters = np.array(map(lambda x: int(kmeans_model.predict(x)), subset_vecs))
    unique_clusters = set(subset_clusters)
    print "number of unique clusters in top {} words: {}.".format(n, len(unique_clusters))
    colormap = discrete_color_scheme(len(unique_clusters))
    int_to_color = {idx: colormap[i] for (i,idx) in enumerate(list(unique_clusters))}
    subset_colors = [int_to_color[i] for i in subset_clusters]
    if embed_style == 'pca':
        pca = PCA(n_components=2)
        pca_embeddings = pca.fit_transform(subset_vecs)
        embed_xs, embed_ys = pca_embeddings.transpose()
    elif embed_style == 'tsne':
        tsne_embeddings = bh_sne(np.asarray(subset_vecs, dtype=np.float64),d=2, perplexity=10)
        embed_xs, embed_ys = tsne_embeddings.transpose()
    fig = plt.figure()
    fig.set_size_inches(50,28.4)
    ax = fig.add_subplot(111)
    ax.scatter(embed_xs, embed_ys, color = subset_colors, s=100)
    for (x,y,word) in zip(embed_xs, embed_ys, subset_words):
        ax.annotate(word, xy=(x,y), textcoords='offset points', fontsize=20)
    plt.title('{} 2d word embeddings'.format(embed_style))
    if savefn is not None:
        plt.savefig(savefn, dpi=120)
    if show:
        plt.show()

def test():
    data_dir = '/Users/jmenick/Desktop/jmAlife/output/models/w2v_50vs_50nc'
    wordvec_fn = '/'.join([data_dir, 'w2v50.word2vec']) 
    kmeans_fn = '/'.join([data_dir, 'kmeans50.pkl'])
    w2v = models.word2vec.Word2Vec.load(wordvec_fn)
    kmeans = joblib.load(kmeans_fn)
    savefn = 'embed_plot_test_tsne.png'
    embedding_fig(w2v, kmeans, embed_style='tsne', savefn=savefn, n=500)

if __name__ == '__main__':
    test()

# visualize a patent's network. 

import networkx as nx
from matplotlib import pyplot as plt
from matplotlib.colors import hex2color
from alife.util.general import load_obj
from alife.util.dbutil import crawl_lineage, subnet_adj_dict
from alife.visualize.discrete_color import discrete_color_scheme
from community.visualize import get_graph
from pymongo import MongoClient

def hex2rgb(hexcolor):
    return hex2color(hexcolor)
#    return [int(c*255) for c in hex2color(hexcolor)]


def network_plot(ancestor_pno, adj, colormap, show=True, savefn=None, title = 'PCA coloring in Patent '):
    # colormap maps from node name to color.
    G = get_graph(adj)
    # defaults to black.
    node_colors = [hex2rgb(colormap.get(node, '#ffffff')) for node in G.nodes()]
    f = plt.figure()
    f.set_size_inches(18.5, 10.5)
    nx.draw_networkx(
        G, 
        nx.spring_layout(G, iterations=20000), 
        #cmap=plt.get_cmap('jet'), 
        node_color=node_colors, 
        node_size=50,
        with_labels = False,
        fontsize=1,
        #font_weight = 'bold',
        linewidths=.5,
        width=.5
    )
    plt.title(title+str(ancestor_pno))
    if savefn is not None:
        print "saving plot..."
        plt.savefig(savefn, dpi=100)
    if show:
        plt.show()
    
def test():
    db = MongoClient().patents
    pno = 4723129
    threshold = 75
    print "getting lineage..."
    lineage = crawl_lineage(
        db, pno, 
        n_generations = 5,
        enforce_func = lambda x: len(x.get('citedby',[])) > threshold,
        flatten = True
    )
    adj = subnet_adj_dict(lineage)
    bubblejet_color_dict_fn = '/Users/jmenick/Desktop/sandbox/jacobs_pca_dicts/bubblejet_pca_dict.p'
    bubblejet_colors = load_obj(bubblejet_color_dict_fn)
    savefn = '{}_force_pca_test.png'.format(pno)
    print "making plot..."
    network_plot(pno, adj, bubblejet_colors, True, savefn)
    return adj, bubblejet_colors

if __name__ == '__main__':
    adj,bjc = test()

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
    G.graph['ancestor'] = ancestor_pno
    ancestor_idx = G.nodes().index(G.graph['ancestor'])
    # defaults to black.
    node_colors = [hex2rgb(colormap.get(node, '#ffffff')) for node in G.nodes()]
    default_node_size = 50
    node_sizes = [default_node_size for node in G.nodes()]
    node_sizes[ancestor_idx] = 6*default_node_size
    f = plt.figure()
    f.set_size_inches(18.5, 10.5)
    nx.draw_networkx(
        G, 
        nx.spring_layout(G, iterations=20000), 
        #cmap=plt.get_cmap('jet'), 
        node_color=node_colors, 
        node_size=node_sizes,
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
        enforce_func = lambda x: len(x.get('citedby',[])) >= threshold,
        flatten = True
    )
    adj = subnet_adj_dict(lineage)
    bubblejet_color_dict_fn = '/Users/jmenick/Desktop/sandbox/jacobs_pca_dicts/bubblejet_pca_dict.p'
    bubblejet_colors = load_obj(bubblejet_color_dict_fn)
    savefn = '{}_force_pca_test.pdf'.format(pno)
    print "making plot..."
    network_plot(pno, adj, bubblejet_colors, True, savefn)
    return adj, bubblejet_colors

def test2():
    db = MongoClient().patents
    family_names = ['stents', 'zeolites', 'bubblejet', 'cellphone', 'pcr', 'microarrays', 'semiconductors', 'nonwovenwebs', 'rsa', 'browser']
    family_pnos = [4655771, 4061724, 4723129, 5103459, 4683202, 
                   5143854, 4064521, 4340563, 4405829, 5572643]
    family_thresholds = [350, 60, 75, 225, 150, 175, 125, 100, 400, 250]
    lilfriend_names = ['skate', 'murphybed', 'hummingbirdfeeder', 'telescopicumbrella', 'hybridengine', 'minesweeper', 'humanoidrobot', 'recumbentbike', 'hangglider', 'ziplock']
    lilfriend_pnos = [6000704, 4766623, 5454348, 4880023, 5191766, 
                      3938459, 6377014, 5284351, 4417707, 6004032]
    lilfriend_thresholds = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    bigfriend_names = ['dentallaser', 'ballisticvest', 'hungryhippos', 'sharkprod', 'gatlinggun', 'nuclearwastetreatment', 'gfp', 'roughterrainchasis', 'bowflex', 'radaraltimeter']
    bigfriend_pnos = [5616141, 4287607, 4119312, 4667431, 4154143, 
                      4274976, 5491084, 4061199, 4725057, 4945360]
    bigfriend_thresholds = [25, 25, 10, 12, 8, 9, 25, 30, 15, 10]
    names = family_names + lilfriend_names + bigfriend_names
    pnos = family_pnos + lilfriend_pnos + bigfriend_pnos
    thresholds = family_thresholds + lilfriend_thresholds + bigfriend_thresholds
    names = names[:1]
    pnos = pnos[:1]
    thresholds = thresholds[:1]
    for pno,threshold,name in zip(pnos, thresholds,names):
        print "getting lineage for patent {} ({}), with threhold {}.".format(pno, name, threshold)
        lineage = crawl_lineage(
            db, pno, 
            n_generations = 5,
            enforce_func = lambda x: len(x.get('citedby',[])) >= threshold,
            flatten = True
        )
        adj = subnet_adj_dict(lineage)
        dict_fn = '/Users/jmenick/Desktop/sandbox/jacobs_pca_dicts/{}_pca_dict.p'.format(name)
        colordict = load_obj(dict_fn)
        savefn = '{}_{}_force_pca_test.pdf'.format(pno, name)
        print "getting plot..."
        network_plot(pno, adj, colordict, False, savefn)
        print "done with {}".format(name)

def main():
    db = MongoClient().patents
    family_names = ['stents', 'zeolites', 'bubblejet', 'cellphone', 'pcr', 'microarrays', 'semiconductors', 'nonwovenwebs', 'rsa', 'browser']
    family_pnos = [4655771, 4061724, 4723129, 5103459, 4683202, 
                   5143854, 4064521, 4340563, 4405829, 5572643]
    family_thresholds = [350, 60, 75, 225, 150, 175, 125, 100, 400, 250]
    lilfriend_names = ['skate', 'murphybed', 'hummingbirdfeeder', 'telescopicumbrella', 'hybridengine', 'minesweeper', 'humanoidrobot', 'recumbentbike', 'hangglider', 'ziplock']
    lilfriend_pnos = [6000704, 4766623, 5454348, 4880023, 5191766, 
                      3938459, 6377014, 5284351, 4417707, 6004032]
    lilfriend_thresholds = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    bigfriend_names = ['dentallaser', 'ballisticvest', 'hungryhippos', 'sharkprod', 'gatlinggun', 'nuclearwastetreatment', 'gfp', 'roughterrainchasis', 'bowflex', 'radaraltimeter']
    bigfriend_pnos = [5616141, 4287607, 4119312, 4667431, 4154143, 
                      4274976, 5491084, 4061199, 4725057, 4945360]
    bigfriend_thresholds = [25, 25, 10, 12, 8, 9, 25, 30, 15, 10]
    names = family_names + lilfriend_names + bigfriend_names
    pnos = family_pnos + lilfriend_pnos + bigfriend_pnos
    thresholds = family_thresholds + lilfriend_thresholds + bigfriend_thresholds
    for pno,threshold,name in zip(pnos, thresholds,names):
        print "getting lineage for patent {} ({}), with threhold {}.".format(pno, name, threshold)
        lineage = crawl_lineage(
            db, pno, 
            n_generations = 5,
            enforce_func = lambda x: len(x.get('citedby',[])) >= threshold,
            flatten = True
        )
        adj = subnet_adj_dict(lineage)
        dict_fn = '/Users/jmenick/Desktop/sandbox/jacobs_pca_dicts/{}_pca_dict.p'.format(name)
        colordict = load_obj(dict_fn)
        savefn = '{}_{}_force_pca_test.pdf'.format(pno, name)
        network_plot(pno, adj, colordict, False, savefn)
        print "done with {}".format(name)
    
if __name__ == '__main__':
    main()

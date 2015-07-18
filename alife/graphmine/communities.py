# detect communities in patents genealogies 
import matplotlib.pyplot as plt
import networkx as nx
from pymongo import MongoClient
from alife.util.dbutil import crawl_lineage, subnet_adj_dict
from alife.mockdb import get_mock
from alife.util.general import pickle_obj
from alife.visualize.patent_vis import network_plot
from community import detect, visualize, util

def community_colors(db, pno, threshold, show_vis = False, savefn=None):
    # Get the patents in the lineage and the adjacency dictionary. 
    lineage = crawl_lineage(
        db, pno, n_generations = 5, 
        enforce_func = lambda x: len(x.get('citedby', [])) >= threshold,
        flatten=True
    )
    adj = subnet_adj_dict(lineage)

    # detect communities
    detector = detect.CommunityDetector(adj)
    communities = detector.run()
    n_communities = len(communities)
    community_lookup = util.get_community_lookup(communities)

    # assign each patent a color, and provide a lookup dictionary
    colors = visualize.discrete_color_scheme(n_communities+1)
    node_color_lookup = {node: colors[community_lookup[node]] for node in adj.keys()}
    
    # make the visualization.
    G = visualize.get_graph(adj)
    G.graph['ancestor'] = pno
    node_colors = [colors[community_lookup[node]] for node in G.nodes()]
    node_colors[G.nodes().index(G.graph['ancestor'])] = colors[n_communities]
    f = plt.figure()
    f.set_size_inches(18.5, 10.5)
    if savefn is not None or show_vis:
        nx.draw_networkx(
            G, 
            nx.spring_layout(G, iterations=20000), 
            cmap=plt.get_cmap('jet'), node_color=node_colors, 
            node_size=65,
            with_labels = False,
            fontsize=1,
#            font_weight = 'bold',
            linewidths=.5,
            width=.5
        )
    if savefn is not None:
        plt.title('Communities in Patent {}'.format(pno))
        plt.savefig(savefn, dpi=100)
    if show_vis:
        plt.show()
    return node_color_lookup

def get_and_save_community_colors(db, pnos, thresholds=None):
    community_colors_list = []
    if thresholds is None:
        thresholds = [0 for _ in pnos]
    for pno,threshold in zip(pnos,thresholds):
        viz_fn = 'viz_'+str(pno)+'.png'
        lookup_fn = 'lookup_'+str(pno)+'.p'
        color_lookup = community_colors(db, pno, threshold, show_vis=False, savefn=viz_fn)
        community_colors_list.append(color_lookup)
        pickle_obj(lookup_fn, color_lookup)
    return community_colors_list

def test():
    db = MongoClient().patents
    pno = 4683202
    threshold = 150
    color_lookup = community_colors(db, pno, threshold, show_vis=False)
    return color_lookup
#    get_and_save_community_colors(db, pnos, thresholds, )

def main():
    db = MongoClient().patents
    family_names = ['stents', 'zeolites', 'bubblejet', 'cellphone', 'pcr', 'microarrays', 'semiconductors', 'nonwovenwebs', 'rsa', 'browser']
    family_pnos = [4655771, 4061724, 4723129, 5103459, 4683202, 5143854, 4064521, 4340563, 4405829, 5572643]
    family_thresholds = [350, 60, 75, 225, 150, 175, 125, 100, 400, 250]
    lilfriend_names = ['skate', 'murphybed', 'hummingbirdfeeder', 'telescopicumbrella', 'hybridengine', 'minesweeper', 'humanoidrobot', 'recumbentbike', 'hangglider', 'ziplock']
    lilfriend_pnos = [6000704, 4766623, 5454348, 4880023, 5191766, 3938459, 6377014, 5284351, 4417707, 6004032]
    lilfriend_thresholds = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    bigfriend_names = ['dentallaser', 'ballisticvest', 'hungryhippos', 'sharkprod', 'gatlinggun', 'nuclearwastetreatment', 'gfp', 'roughterrainchasis', 'bowflex', 'radaraltimeter']
    bigfriend_pnos = [5616141, 4287607, 4119312, 4667431, 4154143, 4274976, 5491084, 4061199, 4725057, 4945360]
    bigfriend_thresholds = [25, 25, 10, 12, 8, 9, 25, 30, 15, 10]
    names = family_names + lilfriend_names + bigfriend_names
    pnos = family_pnos + lilfriend_pnos + bigfriend_pnos
#    thresholds = map(lambda x: x+20, family_thresholds) + lilfriend_thresholds + bigfriend_thresholds
    thresholds = family_thresholds + lilfriend_thresholds + bigfriend_thresholds
    return get_and_save_community_colors(db, pnos, thresholds)

if __name__ == '__main__':
    community_colors_list = main()
    
    


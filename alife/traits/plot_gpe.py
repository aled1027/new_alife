# Plot the GPE results. 
import numpy as np
import matplotlib.pyplot as plt
import sys
from pymongo import MongoClient
from datetime import datetime, timedelta
from matplotlib.dates import date2num
from alife.visualize.discrete_color import discrete_color_scheme
from alife.util.general import load_obj, qtr_year_iter

db = MongoClient().patents
mindate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', 1).limit(1))[0]['isd']
maxdate = list(db.traits.find({'isd': {'$exists': True}}).sort('isd', -1).limit(1))[0]['isd']
maxdate_test = datetime(year=mindate.year+4,month=1,day=1)

def plot_gpe(gpe_data, trait_type, name, out_dir='./', per_trait = True, per_term = True, maxdate = maxdate):
    """
    gpe_data is a dict {trait: [[t1,t2,t3,tot],...]} which maps traits
    to a list of four tuples, where gpe_data[trait]_i is the four price equation 
    terms at time i, the episode of evolution beginning i quarters after the start time. 
    Which, incidentally is q1, 1976. If per_trait, make a plot for each trait, each with all
    the terms. If per_term, make a plot for each term, each with all the traits. 
    """
    assert(trait_type in ['tf-idf', 'docvec'])
    n_traits = len(gpe_data)
    dates = np.array(
        [datetime(yr, month, 1) for yr, month in qtr_year_iter(mindate.year,maxdate.year)]
    )
    traits, serieses = zip(*gpe_data.items())
    dates = dates[5:149] # comment out in normal usage
    
    if per_term:
        scheme = discrete_color_scheme(n=n_traits)
        colormap = {t:scheme[i] for i,t in enumerate(traits)}
        print "making per term full plot..."
        f, (ax1, ax2, ax3, ax4) = plt.subplots(4,1,sharex=True)
        ax1.set_ylabel('GPE Term 1')
        ax1.set_title('Differential Fitness')
        ax2.set_ylabel('GPE Term 2')
        ax2.set_title('Differential Mutation')
        ax3.set_ylabel('GPE Term 3')
        ax3.set_title('Differential Convergence')
        ax4.set_ylabel('Total')
        ax4.set_title('Total Change')
        f.set_size_inches(20.5, 20.5)
        for trait,series in zip(traits, serieses):
#            t1s,t2s,t3s,tots = zip(*series) 
            t1s,t2s,t3s,tots = map(lambda x: x[5:149], zip(*series)) # use previous line in normal use.
            print "dates length: {}, series length: {}".format(len(dates), len(t2s))
            ax2.plot_date(dates, t2s, label=trait, fmt='-',color= colormap[trait])
            ax2.axhline(linewidth=0.1,y=0, color='black')
            ax3.plot_date(dates, t3s, label=trait, fmt='-',color= colormap[trait])
            ax3.axhline(linewidth=0.1,y=0, color='black')
            ax4.plot_date(dates, tots, label=trait, fmt='-',color= colormap[trait])
            ax4.axhline(linewidth=0.1,y=0, color='black')
            ax1.plot_date(dates, t1s, label=trait, fmt='-', color= colormap[trait])
            ax1.axhline(linewidth=0.1,y=0, color='black')
        if n_traits <= 100:
            lgd = plt.legend(bbox_to_anchor=(.5,-0.1, .5, -0.1), loc=9,
                             ncol=4, mode='expand', borderaxespad=0.)
            plt.savefig(out_dir+'gpes_by_term_full_{}_{}.pdf'.format(trait_type, name), dpi=200, bbox_extra_artists=(lgd,), bbox_inches='tight')
        else:
            plt.savefig(out_dir+'gpes_by_term_full_{}_{}.pdf'.format(trait_type, name), dpi=200)

        # Now one for batches.
        batch_size = 12
        n_batches = (len(traits)/batch_size)+1
        for i in range(n_batches):
            scheme = discrete_color_scheme(n=batch_size)
            colormap = {t:scheme[i] for i,t in enumerate(traits[i*batch_size:(i+1)*batch_size])}
            print "making per term batch plots..."
            f, (ax1, ax2, ax3, ax4) = plt.subplots(4,1,sharex=True)
            ax1.set_ylabel('GPE Term 1')
            ax1.set_title('Differential Fitness')
            ax2.set_ylabel('GPE Term 2')
            ax2.set_title('Differential Mutation')
            ax3.set_ylabel('GPE Term 3')
            ax3.set_title('Differential Convergence')
            ax4.set_ylabel('Total')
            ax4.set_title('Total Change')
            f.set_size_inches(20.5, 20.5)
            for trait,series in zip(traits[i*batch_size:(i+1)*batch_size], serieses[i*batch_size:(i+1)*batch_size]):
#                t1s,t2s,t3s,tots = zip(*series)
                t1s,t2s,t3s,tots = map(lambda x: x[5:149], zip(*series)) # use previous line in normal use.
                ax2.plot_date(dates, t2s, label=trait, fmt='-',color= colormap[trait])
                ax2.axhline(linewidth=0.1,y=0, color='black')
                ax3.plot_date(dates, t3s, label=trait, fmt='-',color= colormap[trait])
                ax3.axhline(linewidth=0.1,y=0, color='black')
                ax4.plot_date(dates, tots, label=trait, fmt='-',color= colormap[trait])
                ax4.axhline(linewidth=0.1,y=0, color='black')
                ax1.plot_date(dates, t1s, label=trait, fmt='-', color= colormap[trait])
                ax1.axhline(linewidth=0.1,y=0, color='black')
            lgd = plt.legend(bbox_to_anchor=(.5,-0.1, .5, -0.1), loc=9,
                             ncol=2, mode='expand', borderaxespad=0.)
            plt.savefig(out_dir+'gpes_by_term_batch_{}_{}_{}.pdf'.format(i, trait_type, name), dpi=200, bbox_extra_artists=(lgd,), bbox_inches='tight')

    if per_trait:
        print "making per trait plots..."
        for trait,series in gpe_data.items():
            print "making plot for trait {}".format(trait)
            f = plt.figure()
            f.set_size_inches(18.5, 10.5)
#            t1s, t2s, t3s, tots = zip(*series)
            t1s,t2s,t3s,tots = map(lambda x: x[5:149], zip(*series)) # use previous line in normal use.
            plt.plot_date(dates, t1s, label='diff. fitness', fmt='r-')
            plt.plot_date(dates, t2s, label='diff. mutation', fmt='g-')
            plt.plot_date(dates, t3s, label='diff. convergence', fmt='b-')
            plt.plot_date(dates, tots, label='total change', fmt='y-')
            plt.axhline(linewidth=0.1, y=0, color='black')
            plt.xlabel('Time')
            plt.ylabel('Value')
            plt.title('GPE over time for trait {}'.format(trait))
            plt.legend(loc='upper right')
            plt.savefig(out_dir+'gpe_{}_{}.pdf'.format(trait, name), dpi=100)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit("Usage: python {} <'docvec' or 'tfidf'>  <path to gpe_data pickled dictionary.> <name>".format(sys.argv[0]))
    trait_type = sys.argv[1]
    fn = sys.argv[2]
    name = sys.argv[3]
    data = load_obj(fn)
    plot_gpe(data, trait_type, name)

    

    
        

    
    

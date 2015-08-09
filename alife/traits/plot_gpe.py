# Plot the GPE results. 
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
from alife.visualize.discrete_color import discrete_color_scheme
from alife.util.general import load_obj

def plot_gpe(gpe_data, out_dir='./', per_trait = True, per_term = True):
    """
    gpe_data is a dict {trait: [[t1,t2,t3,tot],...]} which maps traits
    to a list of four tuples, where gpe_data[trait]_i is the four price equation 
    terms at time i, the episode of evolution beginning i quarters after the start time. 
    Which, incidentally is q1, 1976. If per_trait, make a plot for each trait, each with all
    the terms. If per_term, make a plot for each term, each with all the traits. 
    """
    n_traits = len(gpe_data)
    scheme = discrete_color_scheme(n=n_traits)
    colormap = {t:scheme[i] for i,t in enumerate(gpe_data.keys())}
    dates = np.array(
        [datetime(yr, month, 1) for yr, month in qtr_year_iter(mindate.year,maxdate.year)]
    )

    if per_trait:
        print "making per trait plots..."
        for trait,series in gpe_data.items():
            f = plt.figure()
            f.set_size_inches(18.5, 10.5)
            t1s, t2s, t3s, tots = zip(*series)
            plt.plot_date(times, t1s, label='diff. fitness', fmt='r-')
            plt.plot_date(times, t2s, label='diff. mutation', fmt='g-')
            plt.plot_date(times, t3s, label='diff. convergence', fmt='b-')
            plt.plot_date(times, tots, label='total change', fmt='y-')
            plt.xlabel('Time')
            plt.ylabel('Value')
            plt.title('GPE over time for trait {}'.format(trait))
            plt.legend()
            plt.savefig(out_dir+'gpe_{}.pdf'.format(trait), dpi=100)

    if per_term:
        print "making per term plots..."
        f, (ax1, ax2, ax3, ax4) = plt.subplots(4,1,sharex=True)
        ax1.set_ylabel('GPE Term 1')
        ax1.set_title('Differential Fitness')
        ax2.set_ylabel('GPE Term 2')
        ax2.set_title('Differential Mutation')
        ax3.set_ylabel('GPE Term 3')
        ax3.set_title('Differential Convergence')
        ax4.set_ylabel('Total')
        ax4.set_title('Total Change')
        f.set_size_inches(18.5, 10.5)
        for trait,series in gpe_data.items():
            t1s,t2s,t3s,tots = zip(*series)
            ax1.plot_date(times, t1s, label=trait, color= colormap[trait])
            ax2.plot_date(times, t2s, label=trait, color= colormap[trait])
            ax3.plot_date(times, t3s, label=trait, color= colormap[trait])
            ax4.plot_date(times, t4s, label=trait, color= colormap[trait])
        plt.savefig(out_dir+'gpes_by_term.pdf', dpi=100)
   
def test():
    gpes = load_obj('gpes_tfidf_fast_test.p')
    plot_gpe(gpes)

def main():
    print "loading tfidf gpes..."
    gpes_tfidf = load_obj('gpes_tfidf_fast.p')
    print "loading docvec gpes..."
    gpes_docvec = load_obj('gpes_docvec_fast.p')
    print "plotting tfidf gpes..."
    plot_gpe(gpes_tfidf)
    print "plotting docvec gpes..."
    plot_gpe(gpes_docvec)

if __name__ == '__main__':
    test()
    
        

    
    

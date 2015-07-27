# Plot the GPE results. 
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
from alife.visualize.discrete_color import discrete_color_scheme
from alife.util.general import load_obj

def plot_gpe(gpe_data, show=False,savefn=None):
    terms = gpe_data.values()[0].keys()
    term_serieses = {t: [] for t in terms}
    scheme = discrete_color_scheme(n=len(terms))
    colormap = {t:scheme[i] for i,t in enumerate(terms)}
    times = []
    s = sorted(gpe_data.items())
    for date, per_stem_vals in s:
        for stem,val in per_stem_vals.items():
            term_serieses[stem].append(val)
        times.append(date)
    # Now for each stem, we have a list of three-tuples correspnoding to their values over time
    
    # get a 3x1 figure, each sharing the x (time) axis.. 
    f, (ax1, ax2, ax3) = plt.subplots(3,1, sharex= True)
    f.set_size_inches(18.5,10.5)
    for stem,serieses in term_serieses.items():
        ys0 = map(lambda x: x[0], serieses)
        ys1 = map(lambda x: x[1], serieses)
        ys2 = map(lambda x: x[2], serieses)
        ax1.plot_date(times, ys0, color=colormap[stem], label=stem, fmt='b-')
        ax2.plot_date(times, ys1, color=colormap[stem], label=stem, fmt='b-')
        ax3.plot_date(times, ys2, color=colormap[stem], label=stem, fmt='b-')
        
    ax1.set_xlabel('Time')
    ax2.set_xlabel('Time')
    ax3.set_xlabel('Time')
    ax1.set_ylabel('Differential Fecundity')
    ax2.set_ylabel('Differential Mutation')
    ax3.set_ylabel('Differential Convergence')
    ax1.set_title('GPE Term I')
    ax2.set_title('GPE Term II')
    ax3.set_title('GPE Term III')
    handles,labels = ax1.get_legend_handles_labels()
    f.legend(handles, labels,loc='upper right')
    if savefn is not None:
        plt.savefig(savefn, dpi=100)
#    if show:
#        plt.show()

def test():
    gpes = load_obj('gpes_tfidf.p')
    plot_gpe(gpes, savefn='gpes_tfidf_test.pdf')

if __name__ == '__main__':
    test()
    
        

    
    

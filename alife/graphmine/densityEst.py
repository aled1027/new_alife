import numpy as np
import scipy
from scipy import stats
import matplotlib.pyplot as plt
from alife.data import load_file
from alife.visualize.matrix_vis import plot3d
# global
_freq = load_file('frequency_surface')
_exist = load_file('existence_surface')
_prob = load_file('probability_surface')

"""
following tutorial_url: 
http://stackoverflow.com/questions/6620471/fitting-empirical-distribution-to-theoretical-ones-with-scipy-python
"""
def _v_normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    else:
        return v/norm

def _m_normalize(m):
    s = m.sum()
    a = np.asarray(m, dtype=np.float)
    return a/s

def divide_matrices(m1,m2):
    def div(x,y):
        if y == 0:
            return 0
        else:
            return float(x)/y
    return np.array([[div(x1,x2) for x1,x2 in zip(r1,r2)] 
                     for r1,r2 in zip(m1,m2)])

def _divide_vectors(v1,v2):
    def div(x,y):
        if x == 0 or y == 0:
            return 0
        else:
            return float(x)/y
    return np.array([div(xi,yi) for xi,yi in zip(v1,v2)])

def hist_to_full_arr(hist):
    """
    takes an un-normalized histogram and produces the data which 
    gave rise to it. 
    """
    out = []
    for x,count in enumerate(hist):
        for _ in range(count):
            out.append(x)
    return np.array(out)

def fit_1d(data, dist_name):
    try:
        dist = getattr(stats,dist_name)
    except:
        raise RuntimeError("Distribution {} not supported".format(dist_name))
    s = max(data)
    x = np.arange(s)
    param = dist.fit(data)
    return dist.pdf(x, *param[:-2], loc=param[-2], scale=param[-1])

def plot_fitted(data, bins=100, dist_name='gamma', show=True,savefn=None):
    plt.figure()
    plt.hist(data,bins=bins,normed=True)
    plt.plot(fit_1d(data, dist_name))
    if savefn is not None:
        plt.save(savefn, dpi=100)
    if show:
        plt.show()

def just_age(age_cutoff = 1000, ret=True, savefn = None):
    age_freq = _freq.sum(axis=1)[:age_cutoff]
    age_exist = _exist.sum(axis=1)[:age_cutoff]
    age_only_prob = _divide_vectors(age_freq, age_exist)
    f,axarr = plt.subplots(3, sharex = True)
    plt.xlabel('Age in days')
    axarr[0].plot(age_freq)
    axarr[0].set_title('Frequency of Citation given Age of Parent')
    axarr[1].plot(age_exist)
    axarr[1].set_title('Count of Patent/Days with given Age')
    axarr[2].plot(age_only_prob)
    axarr[2].set_title('Probability of citing patent given Age of Parent')
    if savefn is not None:
        plt.savefig(savefn, dpi=100)
    if ret:
        return age_only_prob

def just_pcites(pcites_cutoff = 800, savefn = None, ret = True):
    pcites_freq = _freq.sum(axis=0)[:pcites_cutoff]
    pcites_exist = _exist.sum(axis=0)[:pcites_cutoff]
    pcites_only_prob = _divide_vectors(pcites_freq, pcites_exist)
    f,axarr = plt.subplots(3, sharex = True)
    plt.xlabel('Number of Citations in days')
    axarr[0].plot(pcites_freq)
    axarr[0].set_title('Frequency of Citation given Pcites of Parent')
    axarr[1].plot(pcites_exist)
    axarr[1].set_title('Count of Patent/Days with given cite count')
    axarr[2].plot(pcites_only_prob)
    axarr[2].set_title('Probability of citing patent given Pcites of Parent')
    if savefn is not None:
        plt.savefig(savefn, dpi=100)
    if ret:
        return pcites_only_prob

def main(ret=False, savefn = None):
    print "Getting empricial Age prob and empricial pcites prob..."
    age_prob, pcites_prob = just_age(savefn = 'Empirical Age Probability'), just_pcites(savefn='Empirical Prior Cites Probability')
    mat = np.outer(age_prob, pcites_prob)
    print "Getting 3d surface..."
#    subset = mat[:50,:50]

    plot3d(mat, show=False, plt_type='tri', savefn='empirical_prob_surface_cutoff.png', xlabel='Age of Parent', ylabel='Prior Cites of Parent', title='')
    if savefn is not None:
        plt.savefig(savefn, dpi=100)
    if ret:
        return mat

if __name__ == '__main__':
    main()
    
    

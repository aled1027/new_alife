import numpy as np
import scipy
from scipy import stats
import matplotlib.pyplot as plt
import csv
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D


# global
data_dir = '/Users/jacobmenick/Desktop/alife_refactor/alife/data/surfaces'
freq_fn = '/'.join([data_dir, 'freq_surface.npy'])
exist_fn = '/'.join([data_dir, 'exist_surface.npy'])
prob_fn = '/'.join([data_dir, 'prob_surface.npy'])
freq = np.load(freq_fn)
exist = np.load(exist_fn)[:,:freq.shape[1]]


"""
following tutorial_url: 
http://stackoverflow.com/questions/6620471/fitting-empirical-distribution-to-theoretical-ones-with-scipy-python
"""
def v_normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    else:
        return v/norm

def m_normalize(m):
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

def divide_vectors(v1,v2):
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

def main():
    prob = divide_matrices(freq,exist)
    age_collapse = prob.sum(axis=1)
    pcites_collapse = prob.sum(axis=0)
    
    

#main
"""
data_dir = '/Users/jacobmenick/Downloads'
freqsurface_fn = '/'.join([data_dir, 'frequency_surface.npy'])
arr = np.load(freqsurface_fn)
bigsub = arr[:1000,:100]
#plot3d(bigsub,log=True)
"""
"""
age = arr.sum(axis=1)
pcites = arr.sum(axis=0)
nsample = 30000
y = np.random.choice(hist_to_full_arr(age), size=nsample)
plot_fitted(y)
"""

"""
y2 = np.random.choice(hist_to_full_arr(pcites), size=nsample)
plot_fitted(y2)
"""

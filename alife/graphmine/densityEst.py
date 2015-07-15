import numpy as np
from scipy import stats
from scipy import optimize as opt
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from alife.data import load_file
from alife.visualize.matrix_vis import plot3d, heatmap
# global
_freq = load_file('frequency_surface')
_exist = load_file('existence_surface')
_prob = load_file('probability_surface')

def v_normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    else:
        return v/norm

def divide_matrices(m1,m2):
    """
    Performs elementwise matrix division, being sure to cast inputs to floats
    and return 0 rather than divide by zero. TODO: return np.nan instead. 
    """
    def div(x,y):
        if y == 0:
            # return np.nan
            return 0
        else:
            return float(x)/y
    return np.array([[div(x1,x2) for x1,x2 in zip(r1,r2)] 
                     for r1,r2 in zip(m1,m2)])

def divide_vectors(v1,v2):
    """
    Same as above, but with vectors. 
    """
    def div(x,y):
        if x == 0 or y == 0:
            return 0
        else:
            return float(x)/y
    return np.array([div(xi,yi) for xi,yi in zip(v1,v2)])

def hist_to_full_arr(hist):
    """
    takes an un-normalized histogram and produces the data which 
    gave rise to it. I.e. if we have 5 counts of x, the returned array as [x,x,x,x,x] as a subsequence.
    """
    out = []
    for x,count in enumerate(hist):
        for _ in range(count):
            out.append(x)
    return np.array(out)

def fit_1d(data, dist_name):
    """
    Fit the given one-dimensional distribution to data. Mostly for testing purposes. 
    """
    try:
        dist = getattr(stats,dist_name)
    except:
        raise RuntimeError("Distribution {} not supported".format(dist_name))
    s = max(data)
    x = np.arange(s)
    param = dist.fit(data)
    return dist.pdf(x, *param[:-2], loc=param[-2], scale=param[-1])

def plot_fitted(data, bins=100, dist_name='gamma', show=True,savefn=None):
    """
    Fit the given 1-d distribution *and* plot the fitted distribution against the
    histogram. 
    """
    plt.figure()
    plt.hist(data,bins=bins,normed=True)
    plt.plot(fit_1d(data, dist_name))
    if savefn is not None:
        plt.save(savefn, dpi=100)
    if show:
        plt.show()

## Empirical Model Smoothing

def just_age(age_cutoff = 900, ret=True, savefn = None, show = True):
    """
    Compute the citation frequency, existence counts, and marginal probability
    of a cited parent given age. Optionally plot results 
    """
    age_freq = _freq.sum(axis=1)[:age_cutoff]
    age_exist = _exist.sum(axis=1)[:age_cutoff]
    age_marginal_prob = divide_vectors(age_freq, age_exist)
    if show: 
        # plot frequency, existence, and probability
        f,axarr = plt.subplots(3, sharex = True)
        plt.xlabel('Age in weeks')
        axarr[0].plot(age_freq)
        axarr[0].set_title('Frequency of citation s.t parent has given age')
        axarr[1].plot(age_exist)
        axarr[1].set_title('Count of Patent/weeks with given age')
        axarr[2].plot(age_marginal_prob)
        axarr[2].set_title('Probability of a cited patent having given age')
        if savefn is not None:
            plt.savefig(savefn, dpi=100)
    if ret:
        return age_marginal_prob

def just_pcites(pcites_cutoff = 900, savefn = None, ret = True, show=True):
    """
    Compute the citation frequency, existence counts, and marginal probability
    of a cited parent given prior cites. Optionally plot results 
    """
    pcites_freq = _freq.sum(axis=0)[:pcites_cutoff]
    pcites_exist = _exist.sum(axis=0)[:pcites_cutoff]
    pcites_marginal_prob = divide_vectors(pcites_freq, pcites_exist)
    if show:
        # plot frequency, existence, probability
        f,axarr = plt.subplots(3, sharex = True)
        plt.xlabel('Num. of Citations')
        axarr[0].plot(pcites_freq)
        axarr[0].set_title('Frequency of citation s.t parent has given number of citations')
        axarr[1].plot(pcites_exist)
        axarr[1].set_title('Number of Patent/Weeks with given citation count')
        axarr[2].plot(pcites_marginal_prob)
        axarr[2].set_title('Probability of a cited patent having given number of prior cites.')
        if savefn is not None:
            plt.savefig(savefn, dpi=100)
    if ret:
        return pcites_marginal_prob

def pcites_func(x, gamma, beta):
    """
    The (unnormalized) probability density function which models 
    the marginal probability of citing a parent given in-degree. 
    See Valverde et al. 'attachment kernel'.
    """
    return gamma*(1+beta)*(x**beta)

def weibull(x, shape=1.5, scale=1, c=1):
    """
    A weibull distribution over x. Astonishingly, scipy seems to lack a correct implementation
    of this distribution...?
    """
    shape,scale = map(float, (shape, scale))
    return c*(shape/scale)*((x/scale)**(shape-1))*(np.e**(-1*((x/scale)**shape)))

def fit_empirical_model():
    print "loading data..."
    age_freq = _freq.sum(axis=1)
    age_exist = _exist.sum(axis=1)
    ages = divide_vectors(age_freq, age_exist)
    pcites_freq = _freq.sum(axis=0)
    pcites_exist = _exist.sum(axis=0)
    pcites = divide_vectors(pcites_freq, pcites_exist)
    
    # agex and pcitey are the domains for age and pcites. 
    age_cutoff = 600
    pcites_cutoff = 800
    agex = np.linspace(0, age_cutoff-1, age_cutoff)
    pcitey = np.linspace(0, pcites_cutoff-1, pcites_cutoff)
    x,y = np.meshgrid(np.linspace(0, ages.shape[0]-1, ages.shape[0]), np.linspace(0, pcites.shape[0]-1, pcites.shape[0]))

    # Fit weibull distribution to age dist, preferential attachment kernel to prior cites dist. 
    print "fitting distributions..."
    params_age, pcov_age = opt.curve_fit(weibull, agex, ages[:age_cutoff], p0=[1.765, 596.31, 13.586])
    params_pcites, pcov_pcites = opt.curve_fit(pcites_func, pcitey, pcites[:pcites_cutoff], p0=[0.000655, 1])
    print "Params for Aging Kernel: "
    for p, v in zip(params_age, np.sqrt(np.diag(pcov_age))):
        print p,v
    print "Params for Attachment Kernel: "
    for p,v in zip(params_pcites, np.sqrt(np.diag(pcov_pcites))):
        print p,v

    # assess fit. 
    print "plotting age vs fitted for subset range..."
    x_extrapolate = np.arange(ages.shape[0])
    fitted_age = weibull(x_extrapolate, *params_age)
    f = plt.figure()
    f.set_size_inches(18.5, 10.5)
    plt.plot(ages[:age_cutoff])
    plt.plot(fitted_age[:age_cutoff])
    plt.xlabel('Age')
    plt.ylabel('Un-normalized Probability')
    plt.title('Smoothed (Un-normalized) Probability of a Cited Patent Having a Given Age.')
    plt.savefig('age_fitted.png', dpi=100)
    y_extrapolate = np.arange(pcites.shape[0])
    fitted_pcites = pcites_func(y_extrapolate, *params_pcites)
    print "plotting pcites vs fitted for subset range..."
    f = plt.figure()
    f.set_size_inches(18.5, 10.5)
    plt.plot(pcites[:pcites_cutoff])
    plt.plot(fitted_pcites[:pcites_cutoff])
    plt.xlabel('Num. Citations')
    plt.ylabel('Un-normalized Probability')
    plt.title('(Unnormalized) probability of cited parent having given number of Prior Cites.')
    plt.savefig('pcites_fitted.png', dpi=100)
    print "returning extrapolated fit..."
    return weibull(x, *params_age)*pcites_func(y, *params_pcites)

def main(ret=False, savefn = None):
    print "Getting empricial Age prob and empricial pcites prob..."
    age_prob, pcites_prob = just_age(savefn = 'Empirical_Age_Probability.png'), just_pcites(savefn='Empirical_Prior_Cites_Probability.png')
    print "Fitting Empirical Model..."
    fitted = fit_empirical_model()
    print "saving empirical distribution..."
    np.save('emprical_dist.npy', np.outer(age_prob, pcites_prob))
    print "saving fitted/smoothed empirical distribution..."
    np.save('fitted_empirical_model.npy', fitted)
    print "Plotting empirical model..."
    plot3d(fitted, plt_type='tri', xlabel='Age', ylabel='Prior Cites', title='Smoothed, Un-normalized, Extrapolated Probability Surface a la Valverde', show=False, savefn='fitted_surface.png')

if __name__ == '__main__':
    main()

# This file gives the probability of citation given age and n_cites, according to the parameters we fit to our dataset. 

import numpy as np
y
def attachment_kernel(n_cites, gamma=0.000655460045616, beta=1.0468):
    """
    The (unnormalized) probability density function which models 
    the marginal probability of citing a parent given in-degree. 
    See Valverde et al. 'attachment kernel'.
    """
    return gamma*(1+beta)*(n_cites**beta)

def aging_kernel(age, shape=1.686, scale=737.7, c=17.62):
    """
    A weibull distribution over age. 
    Astonishingly, scipy seems to lack a correct implementation of this distribution...?
    """
    shape,scale = map(float, (shape, scale))
    return c*(shape/scale)*((age/scale)**(shape-1))*(np.e**(-1*((age/scale)**shape)))

def cite_prob(n_cites, age):
    return attachment_kernel(n_cites)*aging_kernel(age)

# EXAMPLE sketch of driving neutral model: 
# patents = [{age: 10, cites: 100}, {age: 5, cites: 200}, ..., {age: 1, cites: 300}]
# unnormalized_probs = [cite_prob(patent['n_cites'], patent['age']) for patent in patents]
# normalization_constant = np.sum(unnormalized_probs)
# probs = unnormalized_probs/float(normalization_constant).
# i = sampled_index(probs)
# return patents[i]

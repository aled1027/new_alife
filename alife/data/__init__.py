import os
import numpy as np

this_dir = os.path.dirname(os.path.realpath(__file__))

surface_locs = {
    'cite_frequency': (np.load, '/'.join([this_dir, 'surfaces/freq_surface.npy'])),
    'existence': (np.load, '/'.join([this_dir, 'surfaces/exist_surface.npy']))
}

def load_surface(name):
    if name in surface_locs:
            
        func,fn = surface_locs[name]
        if name == 'existence':
            return func(fn)[:,:3143]
        else:
            return func(fn)
    else:
        raise RuntimeError('File {} not found'.format(name))

import os
import numpy as np
from alife.util.general import load_obj

this_dir = os.path.dirname(os.path.realpath(__file__))

file_locs = {
    'frequency_surface': (np.load, '/'.join([this_dir, 'surfaces/freq_surface.npy'])),
    'existence_surface': (np.load, '/'.join([this_dir, 'surfaces/exist_surface.npy'])),
    'stem2id': (load_obj, '/'.join([this_dir, 'vocab/stem2id.p']))
}

def load_file(name):
    if name in file_locs:
        func,fn = file_locs[name]
        if name == 'existence_surface':
            return func(fn)[:,:3143]
        else:
            return func(fn)
    else:
        raise RuntimeError('File {} not found'.format(name))

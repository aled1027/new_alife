# General utility functions. 

from itertools import islice

def take(n, iterable)
    # take the first n items from an iterable data structure as a list.
    out = (x for x in islice(iterable, n))
    return list(islice(iterable, n))

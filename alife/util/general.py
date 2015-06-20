# General utility functions. 

from itertools import islice

def take(n, iterable):
    """
    Take the first n items from an iterable data structure as a list.
    If n is more than the number of items in the iterable, just 
    return all of them. 
    """
    assert(n >= 0)
    out = (x for x in islice(iterable, n))
    return list(islice(iterable, n))


# General utility functions.

from itertools import islice, izip, tee
from bson.objectid import ObjectId # crap, we have old pymongo. Need to bring this up to date.
from datetime import datetime, timedelta
import multiprocessing as mp
import cPickle
import numpy as np
import time

_date_fmt_string = "%Y_%m_%d"

def dt_as_str(date_time):
    return date_time.strftime(_date_fmt_string)

def string_to_dt(fmt_string):
    """ Takes a datetime format string in the above format and produces a datetime."""
    year,month,day = map(int, fmt_string.split('_'))
    return datetime(year=year,month=month,day=day)

def step_thru_time(start,end, delta=timedelta(days=7)):
    """ Returns a list of time pairs triples (t-1,t, t+1) which define
    endpoints of intervals of length delta (default 1 week). """
    i = 0
    times = []
    _current_time = start
    nxt1 = start + delta
    nxt2 = start + delta + delta
    while nxt2 < end:
        nxt2 = nxt1 + delta
        times.append((_current_time, nxt1, nxt2))
        _current_time = nxt1
        nxt1 = nxt2
        i += 1
    print "stepped through {} times steps, starting at {} and ending at {}".format(i, start, nxt2)
    return times

def take(n, iterable):
    """
    Take the first n items from an iterable data structure as a list.
    If n is more than the number of items in the iterable, just
    return all of them.
    """
    assert(n >= 0)
    out = (x for x in islice(iterable, n))
    return list(islice(iterable, n))

def save_dict(filename, dictionary):
    """
    Pickle and save a python dictionary at the given location on the filesystem.
    """
    print("warning. save_dict is deprecated. now using pickle_obj.")
    with open(filename, 'wb') as outfile:
        cPickle.dump(dictionary, outfile)

def load_dict(filename):
    """
    Load a pickled python dictionary from the given location on the filesystem.
    """
    print("warning. save_dict is deprecated. now using load_obj.")
    with open(filename, 'rb') as infile:
        return cPickle.load(infile)

def pickle_obj(filename, obj):
    """
    Pickle and save a python dictionary at the given location on the filesystem.
    """
    with open(filename, 'wb') as outfile:
        cPickle.dump(obj, outfile)

def load_obj(filename):
    """
    Load a pickled python dictionary from the given location on the filesystem.
    """
    with open(filename, 'rb') as infile:
        return cPickle.load(infile)

def cosine_dist(v1,v2):
    """
    Computes the cosine distance between two vectors,
    which is 1 - the cosine of the angle between them.
    Recall that <v1,v2> = ||v1|| * ||v2|| * cos(theta)
    """
    cos_ang = np.dot(v1,v2)/(np.linalg.norm(v1)*np.linalg.norm(v2))
    return 1-cos_ang

def euclidean_dist(v1,v2):
    return np.linalg.norm(v1-v2)

def normalize(vector):
    """
    Normalize a vector so that its components sum to 1.
    """
    return vector/np.linalg.norm(vector)

def objid_to_int(objid):
    return int(str(objid), 16)

def int_to_objid(x):
    return ObjectId(hex(x).rstrip("L").lstrip("0x") or "0")

# TODO - These timer utilities should be decorators.
def timeFunc(f):
    start = time.time()
    f()
    end = time.time()
    return (end-start)*1000

def timer(f,n=10):
    times = [timeFunc(f) for _ in range(n)]
    mn = np.min(times)
    mx = np.max(times)
    avg = np.mean(times)
    print "function: {}, min: {}, max: {}, average: {}".format(
        f.__name__, mn,mx,avg
    )

def pairwise_iter(iterable):
    """ Iterate over the iterable in pairs. E.g.
    [1,2,3,4,5] -> (1,2), (2,3), (3,4), ... """
    a,b = tee(iterable)
    next(b,None)
    return izip(a,b)

def month_year_iter(start_year, end_year, start_month=1, end_month=1):
    ym_start= 12*start_year + start_month - 1
    ym_end= 12*end_year + end_month - 1
    for ym in range( ym_start, ym_end ):
        y, m = divmod( ym, 12 )
        yield y, m+1

def qtr_year_iter(start_year, end_year, start_month=1, end_month=1):
    ym_start= 12*start_year + start_month - 1
    ym_end= 12*end_year + end_month - 1
    for ym in range( ym_start, ym_end, 3):
        y, m = divmod( ym, 12 )
        yield y, m+1

def year_year_iter(start_year, end_year, start_month=1):
    """
    generates list of date from start_year to end_year incremented by year
    e.g. [(1980,1),(1981,1),(1982,1) ...]
    """
    ym_start= 12*start_year + start_month - 1
    ym_end= 12*end_year + start_month - 1
    for ym in range(start_year, end_year):
        yield ym, start_month


def step_thru_months(start_yr, end_yr, start_month=1, end_month=1):
    """ produce an iterator of pairs of times, each one month apart. """
    for ((y1,m1), (y2,m2)) in pairwise_iter(month_year_iter(start_yr, end_yr)):
        yield datetime(year=y1,month=m1,day=1), datetime(year=y2,month=m2,day=1)

def step_thru_qtrs(start_yr, end_yr, start_month=1, end_month=1):
    """ produce an iterator of pairs of times, each one quarter apart. """
    for ((y1,m1), (y2,m2)) in pairwise_iter(qtr_year_iter(
            start_yr, end_yr, start_month, end_month
    )):
        yield datetime(year=y1,month=m1,day=1), datetime(year=y2,month=m2,day=1)

def step_thru_years(start_yr, end_yr, start_month=1):
    """ produce an iterator of pairs of times, each one year apart. """
    for ((y1, m1), (y2, m2)) in pairwise_iter(year_year_iter(start_yr, end_yr, start_month)):
        yield datetime(year=y1, month=m1, day=1), datetime(year=y2, month=m2, day=1)

# Parallel map-like function, thanks to stackoverflow. Link below.
# http://stackoverflow.com/questions/3288595/multiprocessing-using-pool-map-on-a-function-defined-in-a-class
def _fun(f,q_in,q_out):
    while True:
        i,x = q_in.get()
        if i is None:
            break
        q_out.put((i,f(x)))

def _fun_verbose(f,q_in,q_out):
    n_processed = 0
    while True:
        i,x = q_in.get()
        if i is None:
            break
        n_processed += 1
        q_out.put((i,f(x)))
    print "processed {} items.".format(n_processed)

def parmap(f, X, nprocs = mp.cpu_count()-1):
    q_in   = mp.Queue(1)
    q_out  = mp.Queue()

    proc = [mp.Process(target=_fun,args=(f,q_in,q_out)) for _ in range(nprocs)]
    for p in proc:
        p.daemon = True
        p.start()

    sent = [q_in.put((i,x)) for i,x in enumerate(X)]
    [q_in.put((None,None)) for _ in range(nprocs)]
    res = [q_out.get() for _ in range(len(sent))]

    [p.join() for p in proc]

    return [x for i,x in sorted(res)]

def parmap_verbose(f, X, nprocs = mp.cpu_count()-1):
    q_in   = mp.Queue(1)
    q_out  = mp.Queue()

    proc = [mp.Process(target=_fun_verbose,args=(f,q_in,q_out)) for _ in range(nprocs)]
    for p in proc:
        p.daemon = True
        p.start()

    sent = [q_in.put((i,x)) for i,x in enumerate(X)]
    [q_in.put((None,None)) for _ in range(nprocs)]
    res = [q_out.get() for _ in range(len(sent))]

    [p.join() for p in proc]

    return [x for i,x in sorted(res)]


# Compute the number of citations over time. 

from alife.mockdb import get_mock
from alife.util.general import save_dict
from pymongo import MongoClient
from collections import Counter
import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import numpy as np

_sentinel_date = datetime.datetime(year=1970,month=1,day=1)

def in_cites_over_time(db, limit=100):
    """
    Returns a list of dates, one for each time a citation of a patent 
    on that date. 
    """
    if limit is not None:
        cites = db.just_cites.find().limit(limit)
    else:
        cites = db.just_cites.find()
    return np.array(
        map(date2num, 
            [cite.get('cited_date', _sentinel_date) for cite in cites]
        )
    )
    

def out_cites_over_time(db, limit=100):
    """
    Return a list of dates, one for each outgoing citation on that date.
    """
    if limit is not None:
        cites = db.just_cites.find().limit(limit)
    else:
        cites = db.just_cites.find()
    return np.array(
        map(date2num, 
            [cite.get('citer_date', _sentinel_date) for cite in cites]
        )
    )

def test():
    db = get_mock()
    in_dates = in_cites_over_time(db)
    out_dates = out_cites_over_time(db)
    f,(ax1, ax2) = plt.subplots(1,2,sharey=True)
    f.set_size_inches(18.5, 10.5)
    ax1.hist(in_dates)
    ax1.set_xlabel('Date')
    ax1.set_title('In-degrees over Time.')
    ax2.hist(out_dates)
    ax2.set_xlabel('Date')
    ax2.set_title('Out-Degrees over Time.')
    return in_dates, out_dates
    
def main():
    ctr_indates = Counter()
    ctr_outdats = Counter()
    db = MongoClient().patents
    in_dates = in_cites_over_time(db, limit = None)
    out_dates = out_cites_over_time(db, limit = None)
    ctr_indates.update(in_dates)
    ctr_outdates.update(out_dates)
    incites_fn = 'incites_over_time_hist.p'
    outcites_fn = 'outcites_over_time_hist.p'
    save_dict(incites_fn, dict(ctr_indates))
    save_dict(outcites_fn, dict(ctr_outdates))
    f,(ax1, ax2) = plt.subplots(1,2,sharey=True)
    f.set_size_inches(18.5, 10.5)
    ax1.hist(in_dates, bins=100)
    ax1.set_xlabel('Date')
    ax1.set_title('In-degrees over Time.')
    ax2.hist(out_dates, bins=100)
    ax2.set_xlabel('Date')
    ax2.set_title('Out-Degrees over Time.')
    plt.savefig('cites_over_time.png')
    

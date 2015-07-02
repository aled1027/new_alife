# Compute the number of citations over time. 

from alife.mockdb import get_mock
from pymongo import MongoClient
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
    ax1.hist(in_dates)
    ax1.set_xlabel('Date')
    ax1.set_title('In-degrees over Time.')
    ax2.hist(out_dates)
    ax2.set_xlabel('Date')
    ax2.set_title('Out-Degrees over Time.')
    return in_dates, out_dates
    
def main():
    db = MongoClient().patents
    in_dates = in_cites_over_time(db, limit = None)
    out_dates = out_cites_over_time(db, limit = None)
    f,(ax1, ax2) = plt.subplots(1,2,sharey=True)
    ax1.hist(in_dates)
    ax1.set_xlabel('Date')
    ax1.set_title('In-degrees over Time.')
    ax2.hist(out_dates)
    ax2.set_xlabel('Date')
    ax2.set_title('Out-Degrees over Time.')
    plt.savefig('cites_over_time.png')
    

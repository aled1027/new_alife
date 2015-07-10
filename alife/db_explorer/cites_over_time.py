# Compute the number of citations over time. 

from alife.mockdb import get_mock
from alife.util.general import save_dict, load_obj
from alife.util.dbutil import get_fields_unordered
from pymongo import MongoClient
from collections import Counter
import datetime
import matplotlib.pyplot as plt
from matplotlib import ticker
from matplotlib.dates import date2num, num2date

_sentinel_date = datetime.datetime(year=1970,month=1,day=1)

def cites_over_time(db, limit=100):
    """
    Returns an incites and outcites counter, a dictionary
    containing the counts of incites,outcites at each date.
    """
    isds,incites,outcites = get_fields_unordered(
        db.patns, 
        ['isd', 'citedby', 'rawcites'], 
        [_sentinel_date, [], []],
        limit
    )
    incite_ctr = Counter()
    outcite_ctr = Counter()
    incite_ctr.update({date:len(cites) for date,cites in zip(isds, incites)})
    outcite_ctr.update({date: len(cites) for date,cites in zip(isds, outcites)})
    return incite_ctr, outcite_ctr

def test():
    db = get_mock()
    inctr, outctr = cites_over_time(db,limit=100)
    in_dates, in_cites = zip(*inctr.items())
    out_dates, out_cites = zip(*outctr.items())
    f,(ax1, ax2) = plt.subplots(1,2,sharey=True)
    f.set_size_inches(18.5, 10.5)
    ax1.scatter(in_dates, in_cites)
    ax1.set_xlabel('Date')
    ax1.set_title('In-degrees over Time.')
    ax2.scatter(out_dates, out_cites)
    ax2.set_xlabel('Date')
    ax2.set_title('Out-Degrees over Time.')
    plt.show()
    return inctr, outctr
    
def main():
    db = MongoClient().patents
    inctr, outctr = cites_over_time(db,limit=None)
    save_dict('inctr.p', dict(inctr))
    save_dict('outctr.p', dict(outctr))
    in_dates, in_cites = zip(*inctr.items())
    out_dates, out_cites = zip(*outctr.items())
    f,(ax1, ax2) = plt.subplots(1,2,sharey=True)
    f.set_size_inches(18.5, 10.5)
    ax1.xaxis.set_major_formatter(ticker.FuncFormatter(lambda numdate, _: num2date(numdate).strftime('%Y-%m')))
    ax1.hist(map(date2num, in_dates), weights=in_cites, bins=150)
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Count')
    ax1.set_title('In-degrees over Time.')
    ax2.xaxis.set_major_formatter(ticker.FuncFormatter(lambda numdate, _: num2date(numdate).strftime('%Y-%m')))
    ax2.hist(map(date2num, out_dates), weights=out_cites, bins=150)
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Count')
    ax2.set_title('Out-Degrees over Time.')
    plt.savefig('cites_over_time.png')
    
if __name__ == '__main__':
    main()

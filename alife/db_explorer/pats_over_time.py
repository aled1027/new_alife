# Compute the number of patents issued over time. 

from alife.mockdb import get_mock
from alife.util import save_dict
from matplotlib.dates import date2num
from collections import Counter
import matplotlib.pyplot as plt
import datetime

_sentinel_date = datetime.datetime(year=1970,month=1,day=1)

def pat_dates(db, limit=100):
    """
    Return a list of dates, one for each patent.
    """
    if limit is not None:
        pats = db.patns.find().limit(limit)
    else:
        pats = db.patns.find()
    return np.array(
        map(dat2num,
        [pats.get('isd', _sentinel_date)]
        )
    )

def test():
    ctr = Counter()
    db = MongoClient().patents
    dates = pat_dates(db)
    outfn = 'pat_isd_histogram.p'
    ctr.update(dates)
    save_dict(outfn, dict(ctr))
    f = plt.figure()
    f.set_size_inches(18.5, 10.5)
    plt.hist(dates, bins=20)
    plt.xlabel('Date')
    plt.ylable('Count')
    plt.title('Number of Patents Issued over Time')
    plt.savefig('pat_isd_histogram.png')


#def main():
#    db = MongoClient().patents
#    dates = pat_dates(db, limit=None)
 
if __name__ == '__main__':
    test()

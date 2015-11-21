from alife.util.general import load_obj
import sys
import os
import csv

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("Usage: python {} <path to .p file>".format(sys.argv[0]))
    else:
        infn = sys.argv[1]
    inbase = os.path.basename(infn)
    outfn = inbase.split('.')[0] + '.csv'

    gpes = load_obj(infn)
    with open(outfn, 'wb') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['trait', 'time_step', 't1', 't2', 't3', 'total'])
        for trait, series in gpes.items():
            for step,term_list in enumerate(series):
                writer.writerow([trait, step]+list(term_list))
        


from collections import defaultdict
from alife.util.general import pickle_obj
import re
import sys

def parseline(line):
    pattern = r"(.+) : INFO : trait: (.+), gpe_terms: (.+)"
    match = re.match(pattern, line)
    if not match:
        return None
    trait,gpes_raw = match.group(2), match.group(3)
    try:
        gpes = map(float, re.sub(r"[()]", "", gpes_raw).split(","))
        return trait, gpes
    except:
        print "there's been a parse error. Line: {}\n, trait: {}, gpes_raw: {}\n)".format(line, trait, gpes_raw)
        sys.exit()


# open the log file in READ mode
def main(infn, outfn, verbose = True):
    
    trait_gpes = defaultdict(list, [])
    with open(infn, 'r') as infile:
        parsed = [x for x in (parseline(line) for line in infile) if x is not None]
    for trait,gpes in parsed:
        if verbose:
            print "{}: {}".format(trait, gpes)
        trait_gpes[trait].append(gpes)
    pickle_obj(outfn, trait_gpes)
        
if __name__ == '__main__':
    infn = 'stuck_gpe.log'
    outfn = 'gpes_fromlog.p'    
    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 2:
        infn = sys.argv[1]
    elif len(sys.argv) == 3:
        infn = sys.argv[1]
        outfn = sys.argv[1]
    else:
        sys.exit("Usage: python {} <infile (optional)> <outfile (optional)>".format(sys.argv[0]))
    main(infn, outfn, verbose = False)
    print "parsed {} and put the result in {}".format(infn, outfn)



    

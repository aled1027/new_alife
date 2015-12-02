import numpy as np
import csv




def go():
    #for key, value in d.iteritems():
    #    (trait_type, trait, gpes, Pa, Pd,X_bar_a, X_bar_d, quotient, absolute_mutations) = value

    src = 'run2gpes_tfidf_3k.p'
    dst = 'gpe_tfidf_year_run2.csv'
    d = np.load(src)

    with open(dst, 'wb') as outfile:
        writer = csv.writer(outfile)
        header = ['trait', 'time_step', 't1', 't2', 't3', 'total', 'Pa', 'Pd', 'X_bar_a', 'X_bar_d', 'absolute_mutations']
        writer.writerow(header)
        j = 0
        for key, value in d.iteritems():
            print(j)
            j += 1
            # removed quotient, in there in some of the pickled files
            (trait_type, trait, gpes, Pa, Pd,X_bar_a, X_bar_d, absolute_mutations) = value
            for i, term_list in enumerate(gpes):
                to_write = [trait, i] + list(term_list) + [Pa[i], Pd[i], X_bar_a[i], X_bar_d[i], absolute_mutations[i]]
                writer.writerow(to_write)

if __name__=='__main__':
    go()




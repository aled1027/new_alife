import numpy as np
import csv


fn = 'gpe_tfidf_year_run2.csv'
with open(fn, 'r') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    d = {}
    for i,row in enumerate(csvreader):
        if i == 0:
            print(row)
            continue
        entry = row[0].split(',')
        if entry[0] in d:
            d[entry[0]].append(entry)
        else:
            d[entry[0]] = [entry]

traits = list(set(list(d.keys())))
for i ,trait in enumerate(traits):
    entries = d[trait]
    for j,_ in enumerate(entries):
        if j == 0:
            entries[j].append(0)
        else:
            real_delta_x = float(entries[j][-2]) - float(entries[j-1][-3])
            entries[j].append(real_delta_x)

dst = 'gpe_tfidf_year_run2_updated.csv'
with open(dst, 'wb') as outfile:
        writer = csv.writer(outfile)
        header = ['trait', 'time_step', 't1', 't2', 't3', 'total', 'Pa', 'Pd', 'X_bar_a', 'X_bar_d', 'absolute_mutations', 'real_delta_x']
        writer.writerow(header)
        j = 0
        for trait, entries in d.iteritems():
            for entry in entries:
                writer.writerow(entry)





def go():
    #for key, value in d.iteritems():
    #    (trait_type, trait, gpes, Pa, Pd,X_bar_a, X_bar_d, quotient, absolute_mutations) = value

    #src = 'run2gpes_tfidf_3k.p'
    src = 'gpe_tfidf_year_run2.p'
    d = np.loadtxt(src)

    with open(dst, 'wb') as outfile:
        writer = csv.writer(outfile)
        header = ['trait', 'time_step', 't1', 't2', 't3', 'total', 'Pa', 'Pd', 'X_bar_a', 'X_bar_d', 'absolute_mutations', 'real_delta_x']
        writer.writerow(header)
        j = 0
        for key, value in d.iteritems():
            print(j)
            j += 1
            # removed quotient, in there in some of the pickled files
            (trait_type, trait, gpes, Pa, Pd,X_bar_a, X_bar_d, absolute_mutations) = value
            prev = None
            for i, term_list in enumerate(gpes):
                real_delta_x = 0 if i==0 else X_bar_d[i] - X_bar_d[i-1]

                to_write = [trait, i] + list(term_list) + [Pa[i], Pd[i], X_bar_a[i], X_bar_d[i], absolute_mutations[i], real_delta_x]
                writer.writerow(to_write)

#if __name__=='__main__':
    #go2()




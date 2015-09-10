## Traits

A module for analyzing traits. Include the Generalized Price Equation, Trait sharing analysis, and utilities for analyzing trait activity over time.

### Running the Temporal GPE calculation
There are three options for running the GPE: `STATIC`, `NONCUM` and `MARK`. In `STATIC` GPE, a the number of children a patent has is static, and equal 
to the total number of citations it has regardless of time. This is mistaken, but is the first way I implemented it, not really thinking. It does enable a massive
speedup though, as we can reuse information about the covariance in term 1 at each timestep. 

Run it in this fashion with 
```python fast_gpe.py STATIC <name>```. 
The script assumes that there is some data precomputed in `alife/traits/precomputed_pops_qtrs_fix`.
It will create a log file `fast_gpe.log` which will indicate progress. The output of the script
is a time series of price equation terms for each trait in the analysis. By default, this is a random sample
of 3000 tfidf traits plus the traits we selected earlier. As a result of running the script, four files will be created;
two each for tfidf and wordvec_clusters as traits. One of these two is a serialized python dictionary whose keys are the 
traits (strings like 'dna' for tfidf and integer indices for wordvec_clusters) and whose values are the time series of gpe terms:

``` {'dna': [(term1, term2, term3, total)_1, (term1, term2, term3, total), ..., (term1, term2, term3, total)_T], 'gpu': [...]} ```

The second is a `.csv` file whose format is indicated in the header. The command line argument `<name>` will prepend the character string `name` to the 
output filenames.

The second fastion `NONCUM`, meaning "non-cumulative" keeps the same ancestral population (namely, all patents issued before time_0), but at each episode of evolution,
considers the number of children a patent has to be *the number of children in the descendant popultion being considered*. 
```python fast_gpe.py NONCUM```. 
It will also create a log file `fast_gpe.log`. This mode does not assume the populations were pre-computed - this would require too much data as the ancestral
population considered both grows and changes at each time step. Even if we are at time t_n, the patents from time t_0 have their child counts updated. So the
only assumption this code makes is that the database server is running.

Finally, we have `MARK`, which implements a mode requested by Mark, in which the ancestral population at each time step is *only those patents which are cited
in the new ancestral population*.
```python fast_gpe.py MARK```. 
It makes the same assumptions as `NONCUM` mode. 

### Plotting GPE results
Once we have performed the compuation above, we can create plots visualizing the results. The plotting script is executed on a per-trait-type basis. 
For instance, regardless of the mode chosen above, I specify as the first option of the script the path to the `.p` file. It will produce `.pdfs` in this 
directory by default. Like the `fast_gpe.py` script above, the parameter `name` will appear in the output filenames.
``` python plot_gpe.py <'tfidf' or 'docvec'>./gpes_tfidf.p <name>```


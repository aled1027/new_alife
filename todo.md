## TODO

___remaining implementations___
*2. Put LDA topics in db. 
*3. Make GPE general accross traits, run it. 
*4. Finish Trait Sharing, make general across traits, run it. 
*5. Grab the data for the market share visualization for Zackary (e.g. trait frequency over time/number of patents over time). 

___good practice___
*1.  Mongomock is used only for unittests. That is, we can't test multithreaded code like parallelMap operations due to python's GIL.
*2.  Set up mongomock so that it has a good sample of documents from reach collection. For instance, the code for testing dooropening
    needs documents that actually have traits and children.
*5. Port ParallelMap, ParallelMapInsert, ParallelMapUpsert into dbutil.
*6. Port the full word2vec pipeline
*7. Write integration tests for the pipeline. Mockdb not useful here because of parallelMap. We need to have a test db for this.
*8. Extensively document the pipeline code. 
*9. Make sure all functions (within reason) have docstrings.
*10. Make sure all modules have documentation (at the very least a readme) and examples.





## TODO

1.  Mongomock is used only for unittests. That is, we can't test multithreaded code like parallelMap operations due to python's GIL.
2.  Set up mongomock so that it has a good sample of documents from reach collection. For instance, the code for testing dooropening
    needs documents that actually have traits and children.
3. For all code, delete global MongoClient() calls. Instead, have functions which access the db take a db input. This way we can unittest everything with mockdb.
   We should only access the real db in __main__ methods.
4. Port RandPat into dbutil.
5. Port ParallelMap, ParallelMapInsert, ParallelMapUpsert into dbutil.
6. Port the full word2vec pipeline
7. Write integration tests for the pipeline. Mockdb not useful here because of parallelMap. We need to have a test db for this.
8. Extensively document the pipeline code. 
9. Make sure all functions (within reason) have docstrings.
10. Make sure all modules have documentation (at the very least a readme) and examples.





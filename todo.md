## TODO

0\*. Produce digests for all of the word2vec models. 
1. For all code, delete global MongoClient() calls. Instead, have functions which access the db take a db input. 
  --> Should default to the mockdb. 
2. Write tests for util/db_util.py
3. Write tests for pipeline
4. Port txtMine modules, refactoring and splitting the model fitting/analysis code by model.
5. Write tests for the txtMine code. 
6. Port txtMine scripts, write tests for them. 
7\*. Run last two lda scripts on markov.
8. Run around making sure all functions have docstrings. 
9. Refactor/port all dbManage scripts into /pipeline, aggregating together the modules and scripts, where each module has a main method which runs the script for everyone in question. 
10. Test and extensively document the pipeline code, building in robust logging. 


\* denotes a script to run, not code to write. 




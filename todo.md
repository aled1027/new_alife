## TODO

### To run:
1. Wait for backup to finish
2. Repair the db. 

####*conventions*
- Only make connections to the database in main methods
- Only really run stuff in main methods, which are invoked if __name__ == 'main'
- Decouple application logic from database access
- Sequester all assumptions about files on disk to alife.data
- Always take a parameter for filename rather than hardcoding one.
- Have good test coverage, but only a sane amount.
- Always take file locations from the command line.
- Have *really* simple examples in readme and more complex examples in /examples
- Make sure db is always the first argument to functions which assume a database.
- Make clear which functions are part of the API and which are private.

### General to do
- Remove commented out, dead code from files
- Make code uniform with regard to conventions above
- Enforce Public/Private API clarity.
- Make this a python package. 
- Document cross-library dependencies
- Compile documentation with sphinx
- Add zackary's code for traitshare

### alife.data
- rename sampler_maps as randpat_data and correct import statements for files that use it.
- add precomputed pops io to alife.data
- Determine if tests are necessary? 
- --> answer: NO
- Update readme
- Make an example. 

### db_explorer
- ensure that the scripts follow the convention of only making real database connections in main 
- Add the code that produces the histogram of patents with the correct fields to this module.
- Bring the scripts into keeping with the command line/filename conventions listed above.
- Determine if tests are necessary?
- --> answer: 
- Update readme
- make an example

### dooropening
- Clean up comments in reach.py
- Fix 'db' position in functions


### graphmine

### mockdb

### pipeline
- reorganize/rename stuff
- decide whether to port the dbManage stuff from jmAlife

### parser
- bring in the files from jmAlife and pypat
- document how the parsing is done. 
- use config file for database stuff.

### traits
- alter precompute_pops to make the number of children be counted per quarter rather than cumulative.
- Make a new version of precompute_pops whicht treats the only ancestors as those which have some child in the current descendant population
- Move precomputed_pops to alife.data

### txtmine
- Bring scripts in line with command line args conventions. 

### util
- Just make sure everything is documented, reasonable stuff is tested (like `alife.util.dbutil.get_fields_unordered()` and `get_field_generator(s)()`)
- Be sure to have a good readme and examples for this file, because it is probably the most used. 
- Be sure it's clear which functions are part of the API and which are private. 

### visualize
- Make sure which files are scripts and which simply helper funces. Document the helper funcs well and make examples.
- No need for tests here.








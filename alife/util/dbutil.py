# Utilities for reading data from mongodb. 
from pymongo import MongoClient

#global
#DB = MongoClient().patents

def get_text(pat, coll_name = 'pat_text'):
    if coll_name == 'pat_text':
        return pat['patText']
    elif coll_name == 'patns':
        text = ''
        if 'title' in pat:
            text += (pat['title'] + ' ')
        if 'abstract' in pat:
            text += pat['abstract']
        return text
    

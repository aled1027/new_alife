# Utilities for reading data from mongodb. 
from pymongo import MongoClient

def get_texts(patents, coll_name = 'pat_text', generator = False):
    """
    Access the text field from an iterable of patent documents.
    """
    require(coll_name in ['pat_text, patns'])
    if coll_name == 'pat_text':
        texts = (pat['patText'] for pat in patents)
    elif coll_name == 'patns':
        texts = (pat['title'] + ' ' + pat['abstract'] for pat in patents)
    else:
        raise RuntimeError('Collection {} not supported, or has no text field'.format(coll_name))
    if generator:
        return texts
    else:
        return list(texts)



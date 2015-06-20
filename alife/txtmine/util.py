# Low level utilities for text mining. 
import string
import re
from nltk.stem.snowball import SnowballStemmer

# Global variables
STEMMER = SnowballStemmer('english')

def is_num(inString):
    # Is the given string a number?
    try:
        float(inString)
        return True
    except:
        return False

def rmv_punc(inString):
    # returns the string with punctuation removed. 
    return ''.join(char for char in inString if char not in set(string.punctuation))

def rmv_numbers(inString):
    # returns the string with numeric chars removed.
    return ''.join(char for char in inString if not char.isdigit())

def mysplit(inString):
    # returns the string split by any amount of whitespace.
    return re.split(u'\s+|\\\\|/', inString)

def rmv_elems_from_list(lst, elems):
    # returns the list with the elements in elems removed. 
    return [x for x in lst if x not in elems]

def stem_words_in_list(lst):
    # returns the list of words, with each word stemmed. 
    return map(STEMMER.stem, lst)


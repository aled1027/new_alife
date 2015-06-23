# A tokenizer. 
from alife.txtmine import util as txtutil
from alife.txtmine import stoplists

english_stops = stoplists.load_stoplist('english')
patent_stops = stoplists.load_stoplist('patents')
all_stops = list(set(english_stops).union(set(patent_stops)))

class Tokenizer(object):
    def __init__(self, replace_hyphens=True, stemming=False, stopwords=all_stops):
        self.replace_hyphens = replace_hyphens
        self.stemming = stemming
        self.stopwords = stopwords

    def tokenize(self, inString):
        if self.replace_hyphens:
            inString = inString.replace('-',' ')
        wo_numpunc = txtutil.rmv_numbers(txtutil.rmv_punc(inString))
        wordlist = map(lambda x: x.lower(), txtutil.mysplit(wo_numpunc))
        if self.stopwords is not None:
            wordlist = txtutil.rmv_elems_from_list(wordlist, self.stopwords)
        if self.stemming:
            wordlist = txtutil.stem_words_in_list(wordlist)
        return wordlist

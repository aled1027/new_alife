# tests the tokenizer. 

import unittest
from alife.txtmine import tokenizer
from alife.txtmine.stoplists import load_stoplist

class TestTokenizer(unittest.TestCase):
    def setUp(self):
        self.short = 'Bi1203498g    D9wg!!!!!!!'
        self.short2 = 'b21234897&*(ig-dog112-34098    play3r'
        self.sentence = 'Hello, the my name is @invention    abstract-patenter, with title and Sh234FS()8((#*t!!    I has a bag---words-bagger. bag-er#fjkl  '
        self.tokenizer = tokenizer.Tokenizer(stopwords=load_stoplist('english'))

    def test_no_spaces(self):
        self.assertTrue('' not in self.tokenizer.tokenize(self.sentence))
        self.assertTrue(' ' not in self.tokenizer.tokenize(self.sentence))

    def test_no_hyphens(self):
        self.assertTrue('-' not in self.tokenizer.tokenize(self.sentence))

    def sanity_check(self):
        self.assertEqual(self.tokenizer.tokenize(self.short), ['big', 'dwg'])

    def test_deals_with_many_spaces(self):
        self.assertEqual(self.tokenizer.tokenize(self.short2), ['big', 'dog', 'playr'])

if __name__ == '__main__':
    unittest.main()
    

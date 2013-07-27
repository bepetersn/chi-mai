import unittest
import re
from chimai.chimai.components.parser import Parser

class ParserTests(unittest.TestCase):

    def setUp(self):
        self.p = Parser()

    def test_depunctuate_simple(self):
        self.assertEqual(self.p.depunctuate("drop the shoe, please"), "drop the shoe please")

    def test_depunctuate_multiple(self):
        self.assertEqual(self.p.depunctuate("drop the shoe, please!"), "drop the shoe please")

    def test_tokenize_and_lower(self):
        self.assertEqual(self.p.tokenize("Drop the sHoe"), ['drop', 'the', 'shoe'])

    def test_drop_tags_are_nonzero_upper_alphabetic(self):
        tags = self.p.find_all_tags('drop')[1]
        self.assertTrue(all([re.match('[A-Z]+', tag) for tag in tags]))

if __name__ == '__main__':
    unittest.main()
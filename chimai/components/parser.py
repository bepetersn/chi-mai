import re
import json
import logging 
import collections
import string

from chimai.chimai.errors import QuitException, FailedParseException, \
UnknownWordException, NoCommandException, HelpException

from treelib.node import Node 
from treelib.tree import Tree

logging.basicConfig(filename='../logs/chimai.log', filemode='w', level='INFO')

def get_rules(f):
    rules = collections.OrderedDict()
    rule_pattern = re.compile("([A-Z]+)\s(?:\+\s([A-Z]+)\s)*->\s([A-Z]+)")
    for line in f.readlines():
        try:
            groups = re.match(rule_pattern, line).groups()
            groups = [group for group in groups if group is not None]
            parts = groups[:-1]
            composite = groups[-1]
            rules[tuple(parts)] = tuple((composite,))
        except AttributeError as e:
            continue

    return rules

class Parser:
        
    def __init__(self):
        self.vocab = {}

        with open('rules.txt') as f:
            self.rules = get_rules(f)

        with open('../vocab/parts_of_speech.json') as f:
            json_string = f.read()
            self.vocab = json.loads(json_string)

    def get_command(self):
        line = raw_input()
        line = self.depunctuate(line)
        tokens = self.tokenize(line)
        tagged_tokens = self.parse(tokens)
        verb, object_name = self.find_verb_and_object(tagged_tokens)
        logging.info("verb: %s, object: %s" % (verb, object))
        return (verb, object_name)

    def tokenize(self, line):
        return line.lower().strip().split(" ")

    def depunctuate(self, line):
        for char in line:
            if char in string.punctuation:
                line = line.replace(char, '')
        return line

    def parse(self, tokens):
        if len(tokens) == 1:
            if tokens[0] == 'quit':
                raise QuitException
            elif tokens[0] == 'help':
                raise HelpException
        multiply_tagged_tokens = self.tag(tokens)
        tree = self.build_valid_sentence_tree(multiply_tagged_tokens)
        singly_tagged_tokens = self.unpack_tree(tree)
        return singly_tagged_tokens

    def tag(self, tokens):
        tagged_tokens = [self.find_all_tags(token) for token in tokens]
        return tagged_tokens

    def find_all_tags(self, token):
        try:
            if not token:
                raise NoCommandException
            elif token[0].isalpha():
                tags = self.vocab[token[0]][token]
            else:
                tags = self.vocab['.'][token]
            tags = sorted(tags, key=lambda t: t[1], reverse=True)
            return (token, [str(tag[0]) for tag in tags])  
        except KeyError:
            raise UnknownWordException(token)

    def build_valid_sentence_tree(self, mtt):

        logging.info("We're gonna build a tree now...")

        tree = Tree()
        above = None
        tokens = [tagged_token[0] for tagged_token in mtt]
        logging.info("tokens: %s" % tokens)
        tagsets = [tagged_token[1] for tagged_token in mtt]
        logging.info("tagsets: %s" % tagsets)
        tagset_lengths = [len(tagset) for tagset in tagsets]
        logging.info("tagset_lengths: %s" % tagset_lengths)
        working = [0 for tagset_length in tagset_lengths]
        logging.info("working: %s" % working)

        for i, tagset in enumerate(tagsets):

            logging.info("tags for word #%s: %s" % (i+1, tagset))
            tree.create_node(tagset[working[i]], tokens[i], parent=above)
            logging.info("creating new node for the word %s..." % tokens[i])
            if i == 0:
                above = tokens[i]
                logging.info("Since this is the first and root node, we're setting all nodes after to be created underneath")
                logging.info("above: %s" % tokens[i])
                logging.info("If this is the last token, we'll just stop here.\n" 
                                "Else, we're gonna look ahead at the tag of the next token, to make some intelligent guesses.")
            if i < len(tagsets)-1:
                logging.info("not the last token!")
                next = tagsets[i+1][working[i]]
                logging.info("looking ahead... tag of next token: %s" % next)
                inter = (self.get_most_likely_rule(next) + ("%s" % i))
                logging.info("based on our lookahead, we're gonna try to use the rule that creates this composite: %s" % inter)
                tree.create_node('inter', inter, parent=above)
                logging.info("we're gonna enter an intermediate node in our tree for that composite")
                above = inter
                logging.info("we're gonna set the new 'above' to be this node too.")
            else:
                logging.info("all done!")
                return tree

    def create_working(self, tagset_lengths, working):
        logging.info("generating a possible tag combination for a set of words.")
        logging.info("length of each tagset: %s", tagset_lengths)
        num_words = len(tagset_lengths)
        logging.info("num words, and thus tags needed: %d", num_words)
        logging.info("last combination of tags used, by indices: %s", working) 
        count = 0
        while True:
            for i in sorted(range(num_words), reverse=True):
                logging.info("index to expect: %d", count)
                logging.info("word we're at: #%d", i+1)
                if working[i] == count:
                    logging.info("this word's tag index is %d", count)
                    logging.info("so we're gonna increment it by one.")
                    logging.info("unless to do so would be creating an impossible combination...")
                    if (tagset_lengths[i] == working[i]+1):
                        if i == 0:
                            logging.info("it's impossible!")
                            return None
                        else:
                            logging.info("gonna try to increment the next word")
                            continue
                    else:
                        logging.info("successfully incremented.")
                        logging.info("now we're gonna return the current working combination")
                        working[i] += 1
                        return working
            logging.info("every index was higher than %d", count)
            logging.info(", so we'll check the next highest integer.")
            count += 1

    def get_most_likely_rule(self, next_token):
        for parts, composite in self.rules.iteritems():
            if parts[0] == next_token:
                return composite[0]

    def unpack_tree(self, tree):

        """
        multiply_tagged_tokens = [('look', ['V', 'N']), ('at', ['P']), ('book', ['N', 'NP', 'V'])]
                                =====>
        tree = ('V', 'look') 
                        -> ('inter', 'PP0',) 
                            -> ('P', 'at') - ('inter', 'OBJ1',)
                                          -> ('N', 'book')
                                =====>
        singly_tagged_tokens = [('look', 'V'), ('at', 'P'), ('book', 'N',)] """


        singly_tagged_tokens = []

        for identifier in tree.expand_tree(mode=Tree.DEPTH):
             node = tree[identifier]
             if node.tag != 'inter':
                 singly_tagged_tokens.append((node.identifier, node.tag))

        return singly_tagged_tokens

    def find_verb_and_object(self, singly_tagged_tokens):
        verb_pos = ['V']
        obj_pos = ['N', 'NP']
        verb = ""
        object = ""
        verb_index = 0
        obj_index = 0

        #concatenate two word objects . . . ?

        for i, (token, tag) in enumerate(singly_tagged_tokens):
            logging.info("%s, %s, %s", i, token, tag)
            if (tag not in verb_pos) and (tag not in obj_pos):
                logging.info("don't care, not a verb or noun")
                continue
            elif tag in verb_pos:
                logging.info("it's a verb!")
                verb = token
                verb_index = i
            elif verb and i != verb_index:
                if tag in obj_pos:
                    logging.info("it's a noun!")
                    object = token
                    obj_index = i
            if verb and i == 0 and len(singly_tagged_tokens) == 1:
                return verb, None

        return verb, object
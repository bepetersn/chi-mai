import re
import json
import logging 
import collections
import string

from chimai.chimai.errors import QuitException, FailedParseException, \
UnknownWordException, NoCommandException, HelpException

from treelib.node import Node 
from treelib.tree import Tree

logging.basicConfig(filename='../logs/chimai.log', filemode='w', level=logging.DEBUG)

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
        logging.debug("verb: %s, object: %s" % (verb, object))
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

    def build_valid_sentence_tree(self, multiply_tagged_tokens):
        logging.info("multiply_tagged_tokens: %s", multiply_tagged_tokens)
        
        tagsets = [word[1] for word in multiply_tagged_tokens]
        logging.info("tagsets: %s", tagsets)

        tagset_lengths = self.get_tagset_lengths(tagsets)
        logging.info("tagset lengths: %s", tagset_lengths)

        working = [0 for tagset in tagset_lengths]
        logging.info("working: %s", working)

        old_working = []
        logging.info("old working: %s", old_working)

        backstack = []
        logging.info("back stack: %s", backstack)

        while True:

            logging.info("starting loopy-loop")
            while True:

                logging.info("finding a possible tag combination")
                possible_tags = self.find_possible_tags(tagsets, working)

                logging.info("multiply tagged tokens: %s", multiply_tagged_tokens)
                logging.info("we're going to try to get a reduced parse")

                logging.info("entering mtt into backstack: %s", backstack)
                backstack.append((multiply_tagged_tokens, working))

                reduced = self.try_to_reduce(possible_tags, multiply_tagged_tokens)
                if reduced:
                    logging.info("backstack: %s", backstack)
                    logging.info("we found a reduced parse: %s", reduced)
                    logging.info("we're going to reset our iterations over the tagsets.")
                                        
                    tagsets = [word[1] for word in reduced]
                    logging.info("tagsets: %s", tagsets)

                    tagset_lengths = self.get_tagset_lengths(tagsets)
                    logging.info("tagset lengths: %s", tagset_lengths)  

                    old_working = working
                    logging.info("old working: %s", old_working)  

                    working = [0 for tagset in tagset_lengths]
                    logging.info("new working: %s", working) 
                   
                    multiply_tagged_tokens = reduced
                    logging.info("mtt: %s", multiply_tagged_tokens)
                    
                    break
                else:
                    logging.info("we didn't find a reduced parse.")
                    logging.info("we're going to go further into our tagsets,"
                        " and generate next possible combination.")
                    working = self.create_working(tagset_lengths, working)

                    while not working:

                        logging.info("shoot, we've tried every possible combination!")
                        logging.info("we have to backtrack!")

                        backstack = self.backtrack(backstack, multiply_tagged_tokens, old_working, 
                            tagsets, tagset_lengths, working)

            if reduced[0][1] == tuple('S'):
                logging.info("we have successfully parsed a sentence!")
                return reduced[0]

    def get_tagset_lengths(self, tagsets):
        tagset_lengths = []
        num_words = len(tagsets)
        for i in range(num_words):
            tagset_lengths.append(len(tagsets[i]))
        return tagset_lengths

    def create_working(self, tagset_lengths, working):
        logging.info("generating a possible tag combination for a set of words.")
        logging.info("length of each tagset: %s", tagset_lengths)

        num_words = len(tagset_lengths)

        logging.info("num words, and thus tags needed: %d", num_words)
        logging.info("last combination of tags used, by indices: %s", working)
                
        x = 0
                
        while True:
            for i in sorted(range(num_words), reverse=True):
                logging.info("index to expect: %d", x)
                logging.info("word we're at: #%d", i+1)

                if working[i] == x:

                    logging.info("this word's tag index is %d", x)
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
            
            logging.info("every index was higher than %d", x)
            logging.info(", so we'll check the next highest integer.")
            x += 1
            
        #NOTE: Leftover from a refactoring confusion. Do I need these lines? 
        #logging.info("working: %s", working)
        #return working

    def find_possible_tags(self, tagsets, working):

        possible_tags = []

        for i, tagset in enumerate(tagsets):

            logging.info("word #: %d", i+1)
            logging.info("tags for the word: %s", tagset)

            possible_tags.append(tagset[working[i]])
                        
            logging.info("select next tag from above tags")
            logging.info("tag #: %d", working[i]+1)
            logging.info("tag: %s", tagset[working[i]])

        logging.info("tagset we're using this time: %s", possible_tags)
        return possible_tags

    def try_to_reduce(self, possible_tags, multiply_tagged_tokens):

        logging.info("we're gonna check against rules;")
        logging.info("if it matches any, we'll return the reduced tagged tokens;")
        logging.info("if it doesn't, we'll drop the leftmost tag...")
        logging.info("until the tags are empty--then we'll try a different possible tagset.")

        while True:
            rule = self.matches_any_rules(possible_tags)
            if not rule:
                logging.info("no match, dropping leftmost tag")
                possible_tags = possible_tags[1:]
                if len(possible_tags) == 0:
                    logging.info("nope, no matching rule")
                    logging.info("try a different tagset")
                    return None
            else:
                logging.info("found a rule that matches")
                logging.info("getting slightly closer parse")
                return self.reduce_by_rule(multiply_tagged_tokens, rule)

    def matches_any_rules(self, tags):
        for parts, composite in self.rules.iteritems():        
            logging.info("%s and %s", tuple(tags), parts)
            if tuple(tags) == parts:
                return (parts, composite)

    def reduce_by_rule(self, multiply_tagged_tokens, rule):
        parts = rule[0]
        logging.info("parts of rule: %s", parts)
        composite = rule[1]
        logging.info("composite of rule: %s", composite)
        end = len(parts)
        logging.info("num tags we're replacing: %s", end)
        length = len(multiply_tagged_tokens)
        logging.info("num tags in the whole sentence: %s", length)
        node = multiply_tagged_tokens[length-end:]
        logging.info("everything we're replacing: %s", node)
        singly_tagged_tokens = []

        #get a copy of mtt rather than a reference to it.
        new_mtt = multiply_tagged_tokens[:]

        for i, tagged_token in enumerate(node):
            singly_tagged = (tagged_token[0], parts[i])
            logging.info("one singly, correctly tagged token: %s", singly_tagged)
            singly_tagged_tokens.append(singly_tagged)
            logging.info("added it to our list of stt's")

        if len(singly_tagged_tokens) == 1:
            child = (singly_tagged, composite)
        else:
            child = ((singly_tagged_tokens[0], singly_tagged_tokens[1]), composite)
        
        for tagged_token in node:
            new_mtt.remove(tagged_token)
            logging.info("new mtt, after removing some stuff: %s", new_mtt)
        
        logging.info("this is what we're adding to mtt in place of what we're removing: %s", child)
        new_mtt.append(child)
        logging.info("new mtt, after adding some stuff: %s", new_mtt)
            
        return new_mtt

    def backtrack(self, backstack, multiply_tagged_tokens, old_working, tagsets, tagset_lengths, working):

        try:
            logging.info("here's our backstack: %s", backstack)
            last_attempt = backstack[-2]
            logging.info("here's our last attempt: %s", last_attempt)
            length = len(backstack)-1
            backstack = backstack[:length]
            logging.info("reset backstack")

        except IndexError:
            logging.error("shoot, we've really tried EVERY possible combination!")
            logging.error("failed to parse this sentence!")
            raise FailedParseException

        multiply_tagged_tokens = last_attempt[0]
        logging.info("mtt: %s", multiply_tagged_tokens)
                                                 
        old_working = last_attempt[1]
        logging.info("old working: %s", old_working)

        tagsets = [word[1] for word in multiply_tagged_tokens]
        logging.info("tagsets: %s", tagsets) 

        tagset_lengths = self.get_tagset_lengths(tagsets)
        logging.info("tagset lengths: %s", tagset_lengths)

        working = self.create_working(tagset_lengths, old_working)
        logging.info("new working: %s", working)

        return backstack

    def unpack_tree(self, tree):

        """

        mtt = [('look', ['V', 'N']), ('at', ['P']), ('book', ['N', 'NP', 'V'])]

        parsed_sentence = (('look', ('V')), ((('at', ('P')), (('book', ('N')), ('OBJ',))), ('PP',)), ('S',))

        tree = ('S',)
            -> ('look', 'V') - ('PP',)
                            -> ('at', 'P') - ('OBJ',)
                                          -> ('book', 'N')

        stt = [('look', 'V'), ('at', 'P'), ('book', 'N',)] """


        singly_tagged_tokens = []

        logging.info("tree: %s", tree)

        logging.info("drop the rightmost tag, 'S' for 'sentence'")
        tree = tree[0]

        logging.info("tree: %s", tree)

        logging.info("checking that two layers down is not a single char,")
        logging.info("in other words, 'tree' is not a simple tuple itself.")
        logging.warning("This will fail with a word like 'a', or 'I'")

        while len(tree[0][0]) != 1:
            
            singly_tagged_tokens.append(tree[0])
            logging.info("added: %s", tree[0])
            
            logging.info("shorten the tree")
            tree = tree[1]
            logging.info("tree: %s", tree)
            
            logging.info("prep tree for next time by dropping rightmost tag, if there is one")
            if len(tree[0][0]) != 1:
                tree = tree[0] 
                logging.info("tree: %s", tree)
                
        logging.info("if tree contains anything, it is the last tagged token.")
        if tree:
            logging.info("so append it to the 'tagged_tokens'.")
            singly_tagged_tokens.append(tree)
            logging.info("added: %s", tree)
            logging.info(singly_tagged_tokens)

        return singly_tagged_tokens

    def find_verb_and_object(self, singly_tagged_tokens):
        verb_pos = ['V']
        obj_pos = ['N', 'NP']
        verb = ""
        object = ""
        verb_index = 0
        obj_index = 0

        #concatenate_two_word_objects(singly_tagged_tokens)

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
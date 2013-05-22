from nltk.corpus import brown as brown
from nltk.corpus import treebank as treebank
import json
import re

brown_tagged_words = brown.tagged_words(simplify_tags=True)
print "brown tags retrieved"

treebank_tagged_words = treebank.tagged_words(simplify_tags=True)
print "treebank tags retrieved"

all_tagged_words = brown_tagged_words + treebank_tagged_words
all_tagged_words = [(tuple[0].lower(), tuple[1]) for tuple in all_tagged_words]
print "all_tags retrieved"

vocab = {}

for char in ".abcdefghijklmnopqrstuvwxyz":
    vocab[char] = {}

for i, (current_word, current_tag) in enumerate(sorted(all_tagged_words)):
    
    if current_word[0] in "abcdefghijklmnopqrstuvwxyz":
        char = current_word[0]
    else:
        char = '.'

    if vocab[char].has_key(current_word):
        try:
            g = [pos[0] for pos in vocab[char][current_word]].index(current_tag)
            vocab[char][current_word][g] = (current_tag, vocab[char][current_word][g][1]+1)
        except ValueError:
            vocab[char][current_word].append((current_tag, 1))
    else:
        vocab[char][current_word] = [(current_tag, 1)]

print "vocab compiled"

with open('frequencies2.txt', 'w') as f:

    data_string = json.dumps(vocab, indent=2)

    f.write(data_string)

print "done writing vocab to file"

"""6.009 Lab 6 -- Autocomplete"""

# NO ADDITIONAL IMPORTS!
from text_tokenize import tokenize_sentences
import pickle
import time

def dictify(t):
    out = {'children': {}, 'value': t.value, }
    for ch, child in t.children.items():
        out['children'][ch] = dictify(child)
    return out
    
class Trie:
    def __init__(self):
        """
        Initialize an empty trie.
        """
        self.value = None
        self.children = {}
        self.type = None
    
    def get_node(self, key):
        """
        used to get the trie at the end of the sequence
        """
        
        # for the given key, return the trie corresponding to ending of the key
        if len(key) == 0:
            return self
        
        if type(key) != self.type:
            raise TypeError
            
        if key[:1] not in self.children:
            return None
        else:
            node = self.children[key[:1]]
            return node.get_node(key[1:])

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.  If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        """
        # when the last element of the key is reached, see if it is assosicated with a value; if yes, return it; if no, raise KeyError
        if len(key) == 0:
            v = self.value
            if v == None:
                raise KeyError
            else:
                return v
        
        if type(key) != self.type:
            raise TypeError
            
        if key[:1] not in self.children:
            raise KeyError
        else:
            node = self.children[key[:1]]
            return node.__getitem__(key[1:])
                
    def __setitem__(self, key, value):
        """
        Add a key with the given value to the trie, or reassign the associated
        value if it is already present in the trie.  Assume that key is an
        immutable ordered sequence.  Raise a TypeError if the given key is of
        the wrong type.
        """
        
        if len(key) == 0:
#            print('a')
            self.value = value
        
        else:
            # for the first element input into the trie, record its type
            if self.type == None:
#                print('b')
                self.type = type(key)

            else:
                if self.type != type(key):
#                    print('c')
                    raise TypeError
                
            if key[:1] not in self.children:
                t = Trie()
                t.type = self.type
                self.children[key[:1]] = t
                
            node = self.children[key[:1]]
            node.__setitem__(key[1:], value)
    
    def __delitem__(self, key):
        self.__setitem__(key, None)

    def __contains__(self, key):
        """
        Return True if key is in the trie and has a value, return False otherwise.
        """
        try:
            self.__getitem__(key)
        except TypeError:
            return False
        except KeyError:
            return False
        else:
            return True

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this trie and
        its children.  Must be a generator or iterator!
        """
        node = self
        def recur_key(node, key_return = None, result = None):
#            print(key_return)
            if key_return == None:
                if self.type == type(''):
                    key_return = ''
                else:
                    key_return = ()
            
            if result == None:
                result = []
                
            if node.value != None:
                result.append((key_return, node.value))
#                print(result)
            
            if node.children != {}:
                for child in node.children:
                    result = recur_key(node.children[child], key_return + child, result)
            return result
            
        return iter(recur_key(node))

def frequency_word(text):
    freq = {}
    s_list = tokenize_sentences(text)
    for sentence in s_list:
        for key in sentence.split(' '):
            if key not in freq:
                freq[key] = 1
            else:
                freq[key] += 1
    return freq

def frequency_sen(text):
    freq = {}
    s_list = tokenize_sentences(text)
    for sentence in s_list:
        if sentence not in freq:
            freq[sentence] = 1
        else:
            freq[sentence] += 1
    return freq

def make_word_trie(text):
    """
    Given a piece of text as a single string, return a Trie whose keys are the
    words in the text, and whose values are the number of times the associated
    word appears in the text
    """
        
    t = Trie()
#    s_list = tokenize_sentences(text)
    freq = frequency_word(text)
    
    freq_list = sorted(freq.items(), key = lambda x: x[1], reverse=True)
    
    for key, value in freq_list:
        t.__setitem__(key, value)
    return t

def make_phrase_trie(text):
    """
    Given a piece of text as a single string, return a Trie whose keys are the
    sentences in the text (as tuples of individual words) and whose values are
    the number of times the associated sentence appears in the text.
    """
    t = Trie()
    s_list = tokenize_sentences(text)
    freq = frequency_sen(text)
    
    for sentence in s_list:
        tuple_sen = tuple(sentence.split(' '))
        t.__setitem__(tuple_sen, freq[sentence])
    return t

def word_in_word(word1, word2):
    for i in range(len(word1)):
        if i == len(word2):
            return False
        if word2[i] == word1[i]:
            continue
        else:
            return False
    return True

def autocomplete(trie, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is of an inappropriate type for the
    trie.
    """
    if type(prefix) != trie.type:
        raise TypeError
        
    new_trie = trie.get_node(prefix)
    if not new_trie:
        return []
    
    iter_word = new_trie.__iter__()
    list_contain = [(prefix + x, y) for (x, y) in iter_word]

    if max_count != None:
        list_contain.sort(key = lambda p: p[1], reverse = True)
        return [p[0] for p in list_contain][:max_count]
                
    else:
        return [p[0] for p in list_contain]
                    
                

def autocorrect(trie, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.

    Do not use a brute-force method that involves generating/looping over
    all the words in the trie.
    """
    # raise NotImplementedError
    comp_words = autocomplete(trie, prefix, max_count)
    if max_count == 0:
        return []
    
    if max_count and len(comp_words) >= max_count:
        #print(comp_words)
        return comp_words[:max_count]
        
    
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    edit = ''
    result = set()
    # insertion
    # insert at 1st place of prefix
    for i in range(len(alphabet)):
        if alphabet[i] in trie.children:
            edit = alphabet[i] + prefix
            if trie.__contains__(edit):
                result.add((edit, trie.__getitem__(edit)))
    
    for i in range(len(prefix)):
        key_f = prefix[:i+1]
        key_b = prefix[i+1:]
        t = trie.get_node(key_f)
        if t:
            for c in t.children:
                edit = key_f + c + key_b
                if trie.__contains__(edit):
                    result.add((edit, trie.__getitem__(edit)))
        else:
            break
    
    # deletion
    for i in range(len(prefix)):
        edit = prefix[:i] + prefix[i+1:]
        if trie.__contains__(edit):
            result.add((edit, trie.__getitem__(edit)))
    
    # replacement
    # replace first element
    for i in range(len(alphabet)):
        if alphabet[i] in trie.children:
            edit = alphabet[i] + prefix[1:]
            if trie.__contains__(edit):
                result.add((edit, trie.__getitem__(edit)))
    
    for i in range(1, len(prefix)):
        key_f = prefix[:i]
        key_b = prefix[i+1:]
        t = trie.get_node(key_f)
        if t:
            for c in t.children:
                edit = key_f + c + key_b
                if trie.__contains__(edit):
                    result.add((edit, trie.__getitem__(edit)))
        else:
            break
    
    # transpose
    for i in range(len(prefix) - 1):
        key_f = prefix[:i]
        key_b = prefix[i+2:]
        edit = key_f + prefix[i+1] + prefix[i] + key_b
        if trie.__contains__(edit):
            result.add((edit, trie.__getitem__(edit)))
    
    if max_count and max_count > len(comp_words):
        result_list = list(result)
        result_list.sort(key = lambda i: i[1], reverse = True)
        return list(set(comp_words + [p[0] for p in result_list][:max_count - len(comp_words)]))
    else:
        return list(set(comp_words + [p[0] for p in list(result)]))

def process_pattern(pattern):
    current_char = ''
    new_p = ''
    for i in range(len(pattern)):
        c = pattern[i]
        if c == '*':
            if current_char == '*':
                continue
            if i >= 2 and pattern[i - 2] == '*' and current_char == '?':
                continue
        current_char = c
        new_p += c
    return new_p
           
def word_filter(trie, pattern):
    """
    Return list of (word, freq) for all words in trie that match pattern.
    pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.

    Do not use a brute-force method that involves generating/looping over
    all the words in the trie.
    """
    '''
    * in pattern: continue search in the trie until find next character
    ? explore the children of trie to find the next character
    '''
    length = 0 
    for i in pattern:
        if i != '*':
            length += 1
    
    pattern = process_pattern(pattern)
    print(pattern)       
    
    def recur_word(trie, pattern, length, match = None, result = None):
        if result == None:
            result = []
    
        if match == None:
            match = ''
        
        plength = 0 
        for i in pattern:
            if i != '*':
                plength += 1
        
        if len(pattern) == 0:
            if trie.value != None and len(match) >= length:
                if (match, trie.value) not in result: 
                    result.append((match, trie.value))
            return result
        
        if pattern[0] == '*':
            if trie.children == {} and len(match) >= length and plength == 0:
                if trie.value != None:
                    if (match, trie.value) not in result:
                        result.append((match, trie.value))
                return result
            # consume star
            for char in trie.children:
                ignore = recur_word(trie, pattern[1:], length, match, result)
                consume = recur_word(trie.children[char], pattern[1:], length, match + char, result)
            # don't consume star
                without_consume = recur_word(trie.children[char], pattern, length, match + char, result)
                if consume:
                    result = consume
                elif ignore:
                    result = ignore
                else:
                    result = without_consume
        
        elif pattern[0] == '?':
            for char in trie.children:
                result = recur_word(trie.children[char], pattern[1:], length, match + char, result)
            
        else:

            if pattern[0] in trie.children:
                return recur_word(trie.children[pattern[0]], pattern[1:], length, match + pattern[0], result)
        
        return result
    
    return recur_word(trie, pattern, length)
# you can include test cases of your own in the block below.
if __name__ == '__main__':
    
    def read_expected(fname):
        with open('tuple_car.pickle', 'rb') as f:
            return pickle.load(f)
    def from_dict(d):
        t = Trie()
        for k, v in d.items():
            t[k] = v
        return t
    
    c = {'make': 'Toyota', 'model': 'Corolla', 'year': 2006, 'color': 'beige'}
    c = {tuple(k): v for k,v in c.items()}
    t = from_dict(c)
    del t[tuple('color')]
#    expect2 = read_expected('tuple_car.pickle')
    result = dictify(t)
    nums = {'thin': [0, 8, 10, None],
                'tom': [0, 2, 4, None],
                'mon': [0, 2, 15, 17, 20, None]}
    with open('Pride and Prejudice.txt', encoding='utf-8') as f:
        text = f.read()
        
    pattern = 'r?c*t'
    w = make_phrase_trie(text)
    result = list(w.__iter__())
    result.sort(key = lambda i: i[1], reverse = True)
    result_4 = [x[0] for x in result[:4]]
    print([x[0] for x in result])
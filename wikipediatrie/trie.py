import unicodedata
import string
import json
import lz4

class TrieUtils:
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    @staticmethod
    def get_key(letter):
        return TrieUtils.letters.index(letter)

    @staticmethod
    def get_letter(key):
        return TrieUtils.letters[key]

    @staticmethod
    def prepare_word(word):
        return ''.join(x for x in unicodedata.normalize('NFKD', word) if x in string.ascii_letters).upper()


class TrieNode:
    def __init__(self):
        self.children = [None] * len(TrieUtils.letters)
        self.occurrences = 0

    def add(self, word, prepare_word=True):
        if prepare_word:
            word = TrieUtils.prepare_word(word)

        if len(word) == 0:
            self.occurrences += 1
            return

        next_key = TrieUtils.get_key(word[0])

        if self.children[next_key] == None:
            self.children[next_key] = TrieNode()

        self.children[next_key].add(word[1:], prepare_word=False)

    def find(self, word, prepare_word=True):
        if prepare_word:
            word = TrieUtils.prepare_word(word)

        if len(word) == 0:
            return self

        next_key = TrieUtils.get_key(word[0])

        if self.children[next_key] == None:
            return None

        return self.children[next_key].find(word[1:], prepare_word=False)

    def get_nodes(self, prefix=""):
        for key, child in enumerate(self.children):
            if child == None:
                continue

            child_prefix = prefix + TrieUtils.get_letter(key)

            if child.occurrences != 0:
                child.word = child_prefix
                yield child

            for node in child.get_nodes(child_prefix):
                yield node

    def get_top_nodes(self, count):
        occurrence_groups = {}
        for node in self.get_nodes():
            key = node.occurrences
            value = occurrence_groups.get(key, []) + [node]
            occurrence_groups[key] = value
        keys = sorted(occurrence_groups.keys(), reverse=True)
        for key in keys:
            for node in occurrence_groups[key]:
                yield node
                count -= 1
                if count == 0:
                    return
            occurrence_groups.pop(key)

    def to_dict(self):
        children = []

        for child in self.children:
            if child:
                children.append(child.to_dict())
            else:
                children.append(None)

        return {
            "children": children,
            "occurrences": self.occurrences
        }

    @staticmethod
    def from_dict(_dict):
        if _dict == None:
            return None

        node = TrieNode()
        node.occurrences = _dict["occurrences"]

        for i, child in enumerate(_dict["children"]):
            node.children[i] = TrieNode.from_dict(child)

        return node

    def to_json(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(string):
        return TrieNode.from_dict(json.loads(string))

    def to_file(self, file):
        data = lz4.compress(self.to_json())
        file.write(data)

    @staticmethod
    def from_file(file):
        json_data = lz4.decompress(file.read()).decode("ascii")
        return TrieNode.from_json(json_data)

    def __lt__(self, other):
        return self.occurrences < other.occurrences

    def __gt__(self, other):
        return self.occurrences > other.occurrences

    def __str__(self):
        if self.word:
            return self.word + " (" + str(self.occurrences) + " ocorrências)"
        else:
            return str(self.occurrences) + " ocorrências"
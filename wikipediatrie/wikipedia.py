from .trie import TrieNode
import pypandoc
import re
import bz2
from xml.sax import parse as parse_sax
from xml.sax.handler import ContentHandler


class TrieBuilder:
    whitespace_regex = re.compile("\W+")

    def __init__(self, file):
        self.file = file
        self.trie = TrieNode()
        self.build_trie()

    def build_trie(self):
        with bz2.BZ2File(self.file, "r") as file:
            parse_sax(file, WikipediaContentHandler(self))

    def add_article(self, source):
        try:
            text = pypandoc.convert_text(source, format="mediawiki", to="plain")
        except:
            text = ""

        for word in TrieBuilder.whitespace_regex.split(text):
            self.trie.add(word)


class WikipediaContentHandler(ContentHandler):
    def __init__(self, trie_builder):
        ContentHandler.__init__(self)
        self.trie_builder = trie_builder
        self.readingText = False

    def startElement(self, name, attrs):
        if name == "text":
            self.readingText = True
            self.text = ""

    def characters(self, content):
        if self.readingText:
            self.text += content

    def endElement(self, name):
        if name == "text":
            self.trie_builder.add_article(self.text)
            self.readingText = False
            self.text = ""
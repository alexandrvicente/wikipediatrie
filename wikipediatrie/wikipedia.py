from .trie import TrieNode
import re
import pypandoc
import bz2
from xml.sax import parse as parse_sax
from xml.sax.handler import ContentHandler
import sys


class TrieBuilder:
    regex = re.compile("\w+", re.U)

    def __init__(self, file):
        self.file = file
        self.trie = TrieNode()
        self.article_count = 0
        self.pandoc = False

    def build_trie(self):
        with bz2.BZ2File(self.file, "r") as file:
            parse_sax(file, WikipediaContentHandler(self))

    def add_article(self, text):
        if self.pandoc:
            try:
                text = pypandoc.convert_text(text, format="mediawiki", to="plain")
            except:
                text = ""
        for word in TrieBuilder.regex.findall(text):
            if len(word) < 256:
                self.trie.add(word)
        self.article_count += 1
        if self.progress_handler:
            self.progress_handler(self.article_count)


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
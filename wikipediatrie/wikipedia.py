from .trie import TrieNode
import re
import pypandoc
import bz2
from xml.sax import parse as parse_sax
from xml.sax.handler import ContentHandler


class TrieBuilder:
    regex = re.compile("\w+", re.U)
    max_word_length = 256
    partial_save_thresold = 10000

    def __init__(self, file):
        self.file = file
        self.trie = TrieNode()
        self.pandoc = False

    def build_trie(self, output_file=None):
        self.output_file = output_file
        with bz2.BZ2File(self.file, "r") as file:
            self.bz2_file = file
            self.articles_to_skip = 0
            self.article_count = 0

            if self.output_file:
                try:
                    self.trie = TrieNode.from_file(self.output_file)
                    if hasattr(self.trie, "progress"):
                        self.articles_to_skip = self.trie.progress
                except:
                    pass

            parse_sax(file, WikipediaContentHandler(self))
            self.bz2_file = None

            if self.output_file:
                delattr(self.trie, "progress")
                self.trie.to_file(output_file)

    def add_article(self, text):
        if self.articles_to_skip != 0:
            self.articles_to_skip -= 1
            self.article_count += 1
            if self.progress_handler:
                self.progress_handler(self.article_count)
            return

        if self.pandoc:
            try:
                text = pypandoc.convert_text(text, format="mediawiki", to="plain")
            except:
                import logging
                logging.error()
                text = ""

        for word in TrieBuilder.regex.findall(text):
            if len(word) < TrieBuilder.max_word_length:
                self.trie.add(word)
        self.article_count += 1

        if self.progress_handler:
            self.progress_handler(self.article_count)

        if self.output_file:
            if self.article_count % self.partial_save_thresold == 0:
                self.trie.progress = self.article_count
                self.trie.to_file(self.output_file)


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
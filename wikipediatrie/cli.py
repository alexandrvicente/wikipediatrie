import click
import bz2
from .wikipedia import TrieBuilder
from .trie import TrieNode

def print_node(node):
    if not node:
        click.secho("Nó não encontrado", fg="red", bold=True, err=True)
        return

    if hasattr(node, "word"):
        click.secho(node.word, nl=False, fg="blue", bold=True)
        click.echo(": ", nl=False)
    click.secho(str(node.occurrences), fg="cyan", nl=False, bold=True)
    click.echo(" ocorrências")

@click.group()
def cli():
    pass

@cli.command()
@click.argument("dump")
@click.argument("trie_file")
def generate(dump, trie_file):
    trie_builder = TrieBuilder(dump)
    with open(trie_file, "wb") as file:
        trie_builder.trie.to_file(file)

@cli.command()
@click.argument("trie_file")
@click.argument("word")
def find(trie_file, word):
    file = open(trie_file, "rb")
    trie = TrieNode.from_file(file)
    node = trie.find(word)
    print_node(node)

@cli.command()
@click.argument("trie_file")
def list(trie_file):
    file = open(trie_file, "rb")
    trie = TrieNode.from_file(file)
    for node in trie.get_nodes():
        print_node(node)

@cli.command()
@click.argument("trie_file")
@click.option("--count", default=10)
def top(trie_file, count):
    file = open(trie_file, "rb")
    trie = TrieNode.from_file(file)
    for node in trie.get_top_nodes(count):
        print_node(node)

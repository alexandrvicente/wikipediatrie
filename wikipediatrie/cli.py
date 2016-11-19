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
@click.option("--pandoc/--regex", default=False)
def generate(dump, trie_file, pandoc):
    trie_builder = TrieBuilder(dump)
    trie_builder.pandoc = pandoc

    def progress_handler(count):
        click.echo("\r" + str(count) + " artigos processados", nl=False)

    trie_builder.progress_handler = progress_handler
    with open(trie_file, "rb+") as file:
        trie_builder.build_trie(file)

@cli.command()
@click.argument("trie_file")
@click.argument("word")
@click.option("--children/--no-children", default=True)
def find(trie_file, word, children):
    file = open(trie_file, "rb")
    trie = TrieNode.from_file(file)
    node = trie.find(word)
    print_node(node)

    if children and sum(1 for n in node.children if n is not None) != 0:
        click.echo("\nFilhos:")
        prefix = word.upper()
        for child in node.get_nodes(prefix=prefix):
            print_node(child)

@cli.command()
@click.argument("trie_file")
def list(trie_file):
    file = open(trie_file, "rb")
    trie = TrieNode.from_file(file)
    for node in trie.get_nodes():
        print_node(node)

@cli.command()
@click.argument("trie_file")
def count(trie_file):
    file = open(trie_file, "rb")
    trie = TrieNode.from_file(file)
    count = 0

    click.echo("0 nós", nl=False)

    for node in trie.get_nodes():
        count += 1
        click.echo("\r" + str(count) + " nós", nl=False)

    click.echo("")


@cli.command()
@click.argument("trie_file")
@click.option("--count", default=10)
def top(trie_file, count):
    file = open(trie_file, "rb")
    trie = TrieNode.from_file(file)

    def progress_handler(count):
        click.echo("\r" + str(count) + " nós processados", nl=False)

    def completion_handler():
        click.echo("")

    top_nodes = trie.get_top_nodes(count, progress_handler, completion_handler)
    for node in top_nodes:
        print_node(node)

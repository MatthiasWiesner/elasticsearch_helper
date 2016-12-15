import re
import json
import click
import elasticsearch
import elasticsearch.helpers
from pprint import pprint

__doc__ = '''
This module helps to interact with Elasticsearch index operations
see API doc: http://elasticsearch-py.readthedocs.org/en/master/api.html#indices
'''


class ElasticsearchClients(object):
    elasticsearchClient = None
    indicesClient = None


@click.group()
@click.option('--hosts', '-h', required=True)
@click.pass_context
def cli(ctx, hosts):
    obj = ElasticsearchClients()
    obj.elasticsearchClient = elasticsearch.Elasticsearch(_split_arg(hosts))
    obj.indicesClient = elasticsearch.client.IndicesClient(
        obj.elasticsearchClient)
    ctx.obj = obj


@cli.command(help='Get aliases for index')
@click.option('-i', '--index', required=True, help='index')
@click.pass_context
def get_aliases(ctx, index):
    print json.dumps(
        ctx.obj.indicesClient.get_aliases([index]),
        indent=2)


@cli.command(help='Delete alias from indexes')
@click.option('-i', '--indexes', required=True, help='indexes (comma separated list)')  # nopep8
@click.option('-a', '--alias', required=True, help='alias')
@click.pass_context
def delete_aliases(ctx, indexes, aliases):
    ctx.obj.indicesClient.delete_alias(
        _split_arg(indexes), _split_arg(aliases))


@cli.command(help='Create alias for indexes')
@click.option('-i', '--indexes', required=True, help='indexes')
@click.option('-a', '--alias', required=True, help='alias')
@click.pass_context
def create_alias(ctx, indexes, alias):
    ctx.obj.indicesClient.put_alias(
        _split_arg(indexes), alias)


@cli.command(help='Move alias from one index to another')
@click.option('-a', '--alias', required=True, help='alias')
@click.option('-f', '--index_from', required=True, help='index from')
@click.option('-t', '--index_to', required=True, help='index to')
@click.pass_context
def move_alias(ctx, alias, index_from, index_to):
    actions = [
        {'remove': {'index': index_from, 'alias': alias}},
        {'add': {'index': index_to, 'alias': alias}}
    ]
    try:
        ctx.obj.indicesClient.update_aliases(dict(actions=actions))
    except elasticsearch.exceptions.ConnectionTimeout as exc:
        print 'We run in a ConnectionTimeout error. Moving the alias is still in process'  # nopep8


@cli.command(help='Create index')
@click.option('-i', '--index', required=True, help='index')
@click.option('-c', '--configuration_file', type=str, required=False, help='Path to the configuration file for the index')  # nopep8
@click.option('--master_timeout', type=int, required=False, help='Specify timeout for connection to master')  # nopep8
@click.option('--timeout', type=int, required=False, help='Explicit operation timeout')  # nopep8
@click.option('--update_all_types', type=bool, required=False, help='Whether to update the mapping for all fields with the same name across all types or not')  # nopep8
@click.pass_context
def create_index(ctx, index, configuration_file, **kwargs):
    kwargs = {k: v for k, v in kwargs.iteritems() if v}
    if configuration_file:
        kwargs['body'] = open(configuration_file).read()
    ctx.obj.indicesClient.create(index, **kwargs)


@cli.command(help='Create Mapping')
@click.option('-i', '--indexes', required=True, help='indexes (comma separated list)')  # nopep8
@click.option('-t', '--doc_type', required=True, help='The name of the document type')  # nopep8
@click.option('-m', '--mapping_file', help='Path to to file with the mapping definition')  # nopep8
@click.option('--allow_no_indices', type=bool, required=False)
@click.option('--expand_wildcards', type=click.Choice(
    ['open', 'closed', 'none', 'all']), required=False)
@click.option('--flat_settings', type=bool, required=False)
@click.option('--ignore_unavailable', type=click.Choice(
    ['missing', 'closed']), required=False)
@click.option('--preserve_existing', type=bool, required=False)
@click.option('--master_timeout', type=int, required=False)
@click.option('--timeout', type=int, required=False)
@click.option('--update_all_types', type=bool, required=False)
@click.pass_context
def change_mapping(ctx, indexes, doc_type, mapping_file, **kwargs):
    kwargs = {k: v for k, v in kwargs.iteritems() if v}
    with open(mapping_file) as f:
        body = f.read()
        ctx.obj.indicesClient.put_mapping(
            doc_type, body, _split_arg(indexes), **kwargs)


@cli.command(help='Delete indexes')
@click.option('-i', '--indexes', required=True, help='indexes (comma separated list)')  # nopep8
@click.pass_context
def delete_index(ctx, indexes):
    ctx.obj.indicesClient.delete(
        _split_arg(indexes))


@cli.command(help='Reindex one index to another (!Experimental, don\'t use it for large indexes)')  # nopep8
@click.option('-f', '--index_from', required=True, help='index from')
@click.option('-t', '--index_to', required=True, help='index to')
@click.pass_context
def reindex(ctx, index_from, index_to):
    elasticsearch.helpers.reindex(
        ctx.obj.elasticsearchClient, index_from, index_to)


def _split_arg(arg):
    return [x for x in re.split('[,\s;:]', arg) if x]


if __name__ == '__main__':
    cli()

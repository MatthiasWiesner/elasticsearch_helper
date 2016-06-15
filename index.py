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
@click.argument('index')
@click.pass_context
def get_aliases(ctx, index):
    print json.dumps(
        ctx.obj.indicesClient.get_aliases([index]),
        indent=2)


@cli.command(help='Delete alias from indexes')
@click.argument('indexes')
@click.argument('aliases')
@click.pass_context
def delete_aliases(ctx, indexes, aliases):
    ctx.obj.indicesClient.delete_alias(
        _split_arg(indexes), _split_arg(aliases))


@cli.command(help='Create alias for indexes')
@click.argument('indexes')
@click.argument('alias')
@click.pass_context
def create_alias(ctx, indexes, alias):
    ctx.obj.indicesClient.put_alias(
        _split_arg(indexes), alias)


@cli.command(help='Move alias from one index to another')
@click.argument('alias')
@click.argument('index_from')
@click.argument('index_to')
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
@click.argument('index')
@click.option('--body', type=str, required=False)
@click.option('--master_timeout', type=int, required=False)
@click.option('--timeout', type=int, required=False)
@click.option('--update_all_types', type=bool, required=False)
@click.pass_context
def create_index(ctx, index, **kwargs):
    kwargs = {k: v for k, v in kwargs.iteritems() if v}
    ctx.obj.indicesClient.create(index, **kwargs)


@cli.command(help='Delete indexes')
@click.argument('indexes')
@click.pass_context
def delete_index(ctx, indexes):
    ctx.obj.indicesClient.delete(
        _split_arg(indexes))


@cli.command(help='Reindex one index to another (!Experimental, don\'t use it for large indexes)')  # nopep8
@click.argument('index_from')
@click.argument('index_to')
@click.pass_context
def reindex(ctx, index_from, index_to):
    elasticsearch.helpers.reindex(
        ctx.obj.elasticsearchClient, index_from, index_to)


def _split_arg(arg):
    return [x for x in re.split('[,\s;:]', arg) if x]


if __name__ == '__main__':
    cli()

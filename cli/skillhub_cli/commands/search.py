"""搜索命令模块"""

import click


@click.command()
@click.argument("query")
def search(query):
    """搜索技能"""
    click.echo(f"正在搜索: {query}")
    # TODO: 实现搜索逻辑

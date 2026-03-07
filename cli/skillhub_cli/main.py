#!/usr/bin/env python3
"""SkillHub CLI 主入口"""

import click

from skillhub_cli.commands import install, publish, search


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """SkillHub - 社区驱动的开放技能平台 CLI 工具"""
    pass


cli.add_command(install.install)
cli.add_command(search.search)
cli.add_command(publish.publish)


if __name__ == "__main__":
    cli()

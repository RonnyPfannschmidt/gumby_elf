from subprocess import call
from glob import glob

import click

from .config import Specification
from .lowlevel import (
    install_develop_data,
    install_extra_requires,
    get_version,
)


@click.group()
@click.pass_context
@click.option(
    '--specification',
    type=click.File('r'), default='package.json')
def main(ctx, specification):
    ctx.obj = Specification(specification)
    ctx.obj.version = get_version()


@main.command()
@click.pass_obj
def develop(obj):
    click.secho("BRAIN HURT", fg='red')
    res = install_develop_data(obj)
    if not res:
        res = install_extra_requires(obj, ['dev'])  # XXX
    if not res:
        click.secho("NO MORE", fg='green')
    else:
        click.secho("MUCH MORE", fg='red')
    return res


@main.command()
def lint():
    call(['flake8', 'src', 'testing'] + glob('*.py'))

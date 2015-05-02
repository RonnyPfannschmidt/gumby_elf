from subprocess import call
from glob import glob

from setuptools_scm import get_version

import click


from .config import Specification
from .lowlevel import (
    install_develop_data,
    install_extra_requires,
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


@main.command()
@click.pass_context
def install(ctx):
    ctx.invoke(build_wheel)
    ctx.invoke(install_wheel)


@main.command()
@click.pass_obj
def build_wheel(obj):
    click.secho("Missing whl build", fg='red', bold=True)


@main.command()
@click.pass_obj
def build_sdist(obj):
    click.secho("Missing sdist build", fg='red', bold=True)


@main.command()
@click.pass_obj
def install_wheel(obj):
    click.secho("Missing whl install", fg='red', bold=True)


@main.command()
@click.pass_context
def dist(ctx):
    ctx.invoke(build_wheel)
    ctx.invoke(build_sdist)

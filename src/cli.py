from os import path, mkdir
from subprocess import call
from glob import glob

from setuptools_scm import get_version

import click


from . import config
from . import packing


@click.group()
@click.pass_context
@click.option(
    '--root',
    type=click.Path(dir_okay=True, file_okay=False, resolve_path=True),
    default='.')
def main(ctx, root):

    ctx.obj = config.read_specification(root)
    ctx.obj.version = get_version()
    if not path.isdir('dist'):
        mkdir('dist')


@main.command()
@click.pass_context
def develop(ctx):
    version = ctx.invoke(build_wheel, develop=True)
    ctx.invoke(install_wheel,
               force_version=version,
               extras='dev')


@main.command()
def lint():
    call(['flake8', 'src', 'testing'] + glob('*.py'))


@main.command()
@click.pass_context
def install(ctx):
    version = ctx.invoke(build_wheel, develop=false)
    ctx.invoke(install_wheel, force_version=version)


@main.command()
@click.pass_obj
@click.option('--develop', is_flag=True)
def build_wheel(obj, develop):
    if develop:
        packing.build_develop_wheel(obj, 'dist')
        return packing.develop_version(obj.version)
    else:
        packing.build_wheel(obj, 'dist')
        return obj.version

@main.command()
@click.pass_obj
def build_sdist(obj):
    click.secho("Missing sdist build", fg='red', bold=True)


@main.command()
@click.pass_obj
@click.option('--force-version')
@click.option('--extras', default=None)
def install_wheel(obj, force_version, extras):
    packagename = '{name}{extras}==={version}'.format(
        name=obj.name,
        version=force_version,
        extras='' if extras is None else '[%s]' % extras
    )
    click.secho('reinstalling ' + packagename, bold=True)
    call(['pip', 'uninstall', packagename, '-yq'])
    call([
        'pip', 'install', packagename,
        '--find-links', 'dist', '-q'])


@main.command()
@click.pass_context
def dist(ctx):
    ctx.invoke(build_wheel)
    ctx.invoke(build_sdist)

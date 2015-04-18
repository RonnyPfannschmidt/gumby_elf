import click
from .config import Specification
from .lowlevel import install_develop_data, install_develop_dependencies

@click.group()
@click.pass_context
@click.option('--specification',
    type=click.File('r'), default='package.json')
def main(ctx, specification):
    ctx.obj = Specification(specification)



@main.command()
@click.pass_obj
def develop(obj):
    click.secho("BRAIN HURT", fg='red')
    install_develop_dependencies(obj)
    install_develop_data(obj)
    click.secho("NO MORE", fg='green')

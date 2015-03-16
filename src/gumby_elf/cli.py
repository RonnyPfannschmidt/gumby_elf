import click


@click.group()
def main():
    pass



@main.command()
def develop():
    click.secho("BRAIN HURT", fg='red')

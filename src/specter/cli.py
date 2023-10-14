"""
The main cli execution
"""
import click
from . import __version__

def ver():
    """
    Shows program version
    """
    click.echo(__version__)

@click.group(invoke_without_command=True, no_args_is_help=True)
@click.option('-v','--version', is_flag=True, help="Show version")
@click.pass_context
def cli(ctx, version):
    ctx.ensure_object(dict)
    if version:
        ver()

@cli.command()
def stop():
    click.echo("Stop the execution")

@cli.command()
def hello():
    click.echo("Hello World Click!")

if __name__ == '__main__':
    cli(obj={})

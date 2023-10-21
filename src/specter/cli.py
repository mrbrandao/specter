"""
The main cli execution
"""
from typing import Optional
import click
from . import formater, crate, packages, __version__

def ver():
    """
    Shows program version
    """
    click.echo(__version__)

@click.group(invoke_without_command=True, no_args_is_help=True)
@click.option('-v','--version', is_flag=True, help="Show version")
@click.pass_context
def cli(ctx, version):
    """
    cli is the main execution function
    """
    ctx.ensure_object(dict)
    if version:
        ver()

@cli.command()
@click.option('-i','--input','input_',
              default='/tmp/test', help='Path to input file',
              show_default=True
              )
@click.option('-b','--branch', default='f38',
              show_default=True,
              help='Define the mdapi branch to search'
              )
@click.option('-l','--list','list_', is_flag=True,help='List dependencies')
@click.option('-o','--out', default='specter-search.json',help='Save the search file')
@click.pass_context
def search(_ctx: click.Context, **kwargs):
    """
    Search for package dependencies
    """
    click.echo(f'searching {kwargs["input_"]}')
    click.echo(f'searching {kwargs}')
    pkgs = packages.parse(kwargs['input_'])
    crate.crate_to_rpm(pkgs)

    if kwargs['list_']:
        sizes = formater.header()
        for pkg in pkgs:
            pkg['avaver'] = "Not Searched"
            pkg['status'] = "MISS"
            formater.info(sizes, pkg)
    else:
        packages.search(kwargs, pkgs)

@cli.command()
@click.option('-i','--input','input_',
              default='specter-search.json', help='Path to input file',
              show_default=True
              )
@click.pass_context
def requires(_ctx: click.Context, **kwargs):
    """
    Generate the BuildRequires list
    """
    packages.generate_requires(kwargs['input_'])

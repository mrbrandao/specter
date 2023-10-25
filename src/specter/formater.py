""" 
    formater:
        format tables, lists and headers
"""
from rich.console import Console

console = Console(highlight=False)

# pylint: disable=R0903
class Colors:
    """
    Declares the custom colors
    """
    green = "#00d700"
    red = "#ff5555"
    yellow = "#abd102"

def header():
    """
    header:
        creates a formated header to be used while printing on stdout
    """
    sizes = {'name': 45,'minver': 10,'maxver': 10, 'avaver': 15, 'status': 8}
    head = (f"{'Package Name':<{sizes['name']}}"
    f"{'Min Ver':<{sizes['minver']}}"
    f"{'Max Ver':<{sizes['maxver']}}"
    f"{'Available Ver':<{sizes['avaver']}}"
    f"{'Status':<{sizes['status']}}")
    console.print(head)
    return sizes

def info(sizes, pkg):
    """
    info:
        receives a package and print the info for it
    """
    status = f"[{Colors.red}]{pkg['status']:<{sizes['status']}}[/]"
    avaver = f"{pkg['avaver']:<{sizes['avaver']}}"

    if pkg['status'] in 'FOUND':
        status = f"[{Colors.green}]{pkg['status']:<{sizes['status']}}[/]"
    elif pkg['avaver'] in 'MISS':
        avaver = f"[{Colors.yellow}]{pkg['avaver']:<{sizes['avaver']}}[/]"

    content = (
    f"{pkg['rpm_name']:<{sizes['name']}}"
    f"{pkg['minver']:<{sizes['minver']}}"
    f"{pkg['maxver']:<{sizes['maxver']}}"
    f"{avaver}"
    f"{status}")
    console.print(content)

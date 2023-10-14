#!/usr/bin/env python3
""" 
    formater:
        format tables, lists and headers
"""

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
    print(head)
    return sizes

def info(sizes, pkg):
    """
    info:
        receives a package and print the info for it
    """
    content = (
    f"{pkg['rpm_name']:<{sizes['name']}}"
    f"{pkg['minver']:<{sizes['minver']}}"
    f"{pkg['maxver']:<{sizes['maxver']}}"
    f"{pkg['avaver']:<{sizes['avaver']}}"
    f"{pkg['status']:<{sizes['status']}}")
    print(content)

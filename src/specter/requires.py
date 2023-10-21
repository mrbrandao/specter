"""
render the requires command 
"""
import json
from . import formater

def load_file(in_file):
    """
    receive a JSON file and return a JSON loaded
    """
    with open(in_file, 'r', encoding='utf-8') as file:
        requires_list = json.load(file)
    return requires_list

def generate(in_file):
    """
    receive a json file and print the BuildRequires to stdout
    """
    requires_list = load_file(in_file)
    for requires in requires_list:
        print(f"BuildRequires:  \
{requires['rpm_name']} {requires['minsig']} {requires['minver']}, \
{requires['rpm_name']} {requires['maxsig']} {requires['maxver']}")

def do_list(in_file):
    """
    receive a specter JSON file and print it's content
    """
    pkgs = load_file(in_file)
    sizes = formater.header()
    for pkg in pkgs:
        formater.info(sizes, pkg)

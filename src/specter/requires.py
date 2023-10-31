"""
render the requires command 
"""
import json
import pyperclip
from . import formater

def load_file(in_file):
    """
    receive a JSON file and return a JSON loaded
    """
    with open(in_file, 'r', encoding='utf-8') as file:
        requires_list = json.load(file)
    return requires_list

def generate(in_file, clip):
    """
    receive a json file and print the BuildRequires to stdout
    """
    requires_list = load_file(in_file)
    current_clip = ''
    if clip:
        formater.console.print(
                f'[{formater.Colors.yellow}][i]Copying to clipboard,[/]'
                '[i]paste it in your spec file under the '
                f'[bold {formater.Colors.green}]BuildRequires [/]'
                f'[{formater.Colors.yellow}]session...[/]')
    for requires in requires_list:
        out = ('BuildRequires: '
               f'{requires["rpm_name"]} {requires["minsig"]} {requires["minver"]}')
        if requires['minsig'] not in '=':
            out = ('BuildRequires: '
                f'{requires["rpm_name"]} {requires["minsig"]} {requires["minver"]}, '
                f'{requires["rpm_name"]} {requires["maxsig"]} {requires["maxver"]}')
        print(out)
        if clip:
            if current_clip != '':
                current_clip = current_clip + '\n' + out
            else:
                current_clip = out
            pyperclip.copy(current_clip)

def do_list(in_file):
    """
    receive a specter JSON file and print it's content
    """
    pkgs = load_file(in_file)
    sizes = formater.header()
    for pkg in pkgs:
        formater.info(sizes, pkg)

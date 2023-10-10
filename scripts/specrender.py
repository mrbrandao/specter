#!/usr/bin/env python3
"""render templates to create README files"""

import argparse, os
from jinja2 import Environment, FileSystemLoader

def render(args):
    dirs, file = os.path.split(args.path)
    environment = Environment(loader=FileSystemLoader(dirs))
    template = environment.get_template(file)
    dest = args.dest
    content = template.render(
        vmin=args.min,
        package_name=args.name,
        package_version=args.ver,
        requires=args.requires,
    )
    with open(dest, mode="w", encoding="utf-8") as message:
        message.write(content)
        print(f"... wrote {dest}")

def main():
    home = os.environ['HOME']
    parser = argparse.ArgumentParser(description='Render a README')
    parser.add_argument('requires', metavar='N', type=str, nargs='+',
                        help='one or multiple package requires')
    parser.add_argument('--name', help='package name')
    parser.add_argument('--ver', default='', help='package version')
    parser.add_argument('--dest', default='README.md', help='filename dest')
    parser.add_argument('--path',
    default=f'{home}/dev/gen/specter/templates/rust_readme.j2', help='template source to be used')
    parser.add_argument('--min', action='store_true', help='if used will use version in the spec files')
    args = parser.parse_args()
    #print(args)
    render(args)

main()

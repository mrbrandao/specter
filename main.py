#!/usr/bin/env python3
"""
Specter aims to find missing dependencies to build a RPM package
"""

import subprocess
from specter.cmd import formater
from specter.cmd.arguments import flags
from specter.packages import packages,crate

def run_rpmbuild(input_file):
    cmd = [
        'rpmbuild',
        '-ba',
        input_file
        ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return result.stderr

def main():
    """
    main script execution
    """
    args = flags()
    in_file = args.input
    pkgs = packages.parse(in_file)
    new = crate.crate_to_rpm(pkgs)

    if args.list:
        sizes = formater.header()
        for pkg in pkgs:
            pkg['avaver'] = "Not Searched"
            pkg['status'] = "MISS"
            formater.info(sizes, pkg)

    if args.search:
        packages.search(args, pkgs)

if __name__ == "__main__":
    main()

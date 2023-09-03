#!/usr/bin/env python3
"""
Specter aims to find missing dependencies to build a RPM package
"""

import subprocess
import argparse
import re
import time
import requests

def create_header():
    """
    create_header:
        creates a formated header to be used while printing on stdout
    """
    under_header = ""
    sizes = {'name': 45,'minver': 10,'maxver': 10, 'avaver': 15}
    header = (f"{'Package Name':<{sizes['name']}}"
    f"{'Min Ver':<{sizes['minver']}}"
    f"{'Max Ver':<{sizes['maxver']}}"
    f"{'Available Ver':<{sizes['maxver']}}")
    print(header)
    print(f"{'*' * sum(sizes.values())}")
    return sizes

def run_rpmbuild(input_file):
    cmd = [
        'rpmbuild',
        '-ba',
        input_file
        ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return result.stderr

def packages(in_file):
    """
    packages:
        receives the input file and returns a list of packages
    """
    pkgs = []
    sigs = r'[=<>]'
    with open(in_file, "r", encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            values = line.split()
            name = values[0]
            minsig = ""
            minver = ""
            maxsig = ""
            maxver = ""
            if len(values) > 5:
                minver = values[2]
                if re.search(sigs,values[1]):
                    minsig = values[1]
                maxver = values[6].replace('~)',"")
                if re.search(sigs,values[5]):
                    maxsig= values[5]
            pkg = {"name": name, "minsig": minsig, "minver": minver,
                  "maxsig": maxsig, "maxver": maxver }
            pkgs.append(pkg)
    return pkgs

def crate_name_converter(pkgs):
    """
    crate_name_converter:
        receives a list of packages and returns a the list appending the
        converted RPM name
        e.g: (crate(foo/default) converts to rust-foo+default-devel
    """
    for pkg in pkgs:
        name = pkg["name"].replace("/",
        "+").strip('()').replace('crate(','rust-')
        pkg['rpm_name'] = f"{name}-devel"
    return pkgs

def package_info(sizes, pkg):
    """
    package_list:
        receives a package and print the info for it
    """
    content = (
    f"{pkg['rpm_name']:<{sizes['name']}}"
    f"{pkg['minver']:<{sizes['minver']}}"
    f"{pkg['maxver']:<{sizes['maxver']}}"
    f"{pkg['avaver']:<{sizes['avaver']}}")
    print(content)

def version_define(number):
    """
    version_define:
        receives a version number and returns parsed version for a package
        e.g: 0.1.0 == 0.1
             1.2.3 == 1
    """
    if not number.startswith('0'):
        return number.split('.')[0]

    number = number.split('.')
    return f'{number[0]}.{number[1]}'

def add_package_version(pkg, version):
    """
    add_package_version:
        add a version into the package name
        e.g: rust-clap+default-devel == rust-clap2+default-devel
             rust-clap-devel == rust-clap2-devel
    """
    sigs = r'[+]'
    if not re.search(sigs,pkg):
        return pkg.replace('-devel',f'{version}-devel')
    return pkg.replace('+',f'{version}+')

def package_search(args, pkgs):
    """
    package_search:
        search a package using mdapi
        receives argparse arguments and the packages list 
        returns the modified packages list with the available package version
    """
    url = "https://mdapi.fedoraproject.org/"
    branch = args.branch
    sizes = create_header()
    for pkg in pkgs:
        pkg_name = pkg['rpm_name']
        req = f"{url}{branch}/pkg/{pkg_name}"
        response = requests.get(req,timeout=10)
        #print(version)
        #print(response.text)
        if response.status_code != 200:
            version = version_define(pkg['minver'])
            pkg_name = add_package_version(pkg['rpm_name'],version)
            req = f"{url}{branch}/pkg/{pkg_name}"
            response = requests.get(req,timeout=10)
            if response.status_code != 200:
                pkg['avaver'] = 'MISS'
                time.sleep(1)
                package_info(sizes,pkg)
                continue
            data = response.json()
            pkg['avaver'] = data['version']
            pkg['rpm_name'] = pkg_name
        data = response.json()
        pkg['avaver'] = data['version']
        time.sleep(1)
        package_info(sizes, pkg)
    return pkgs

def arguments():
    """
    arguments:
        define the argparse flags and parameters
        returns the parsed arguments
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-i", 
        "--input", 
        help="Path to the input file",
        default="/tmp/test"
        )
    parser.add_argument(
        "-l",
        "--list",
        action='store_true',
        help="List dependency packages and versions"
        )
    parser.add_argument(
        "-b",
        "--branch",
        default="f38",
        help="Define the mdapi branch"
        )
    parser.add_argument(
        "-s",
        "--search",
        action='store_true',
        help="Search packages using mdapi"
        )

    args = parser.parse_args()
    return args

def main():
    """
    main script execution
    """
    args = arguments()
    in_file = args.input
    pkgs = packages(in_file)
    new = crate_name_converter(pkgs)

    if args.list:
        sizes = create_header()
        for pkg in pkgs:
            pkg['avaver'] = "Not Searched"
            package_info(sizes, pkg)
    if args.search:
        package_search(args, pkgs)

if __name__ == "__main__":
    main()

"""
packages:
    manipulate package data
"""
import re
import time
import json
import requests
from pkg_resources import parse_version
from . import formater

def parse(in_file):
    """
    parse:
        receives the input file and returns a parsed list of packages
    """
    pkgs = []
    sigs = r'[=<>]'
    version_pattern = r'^\d.{2,}'
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
                if re.match(version_pattern,values[2]):
                    minver = values[2]
                if re.search(sigs,values[1]):
                    minsig = values[1]
                if re.match(version_pattern,values[6]):
                    maxver = values[6].replace('~)',"")
                if re.search(sigs,values[5]):
                    maxsig= values[5]
                if minver != '' and maxver == '' and minsig in '=':
                    maxver=minver
            pkg = {"name": name, "minsig": minsig, "minver": minver,
                  "maxsig": maxsig, "maxver": maxver }
            pkgs.append(pkg)
    return pkgs

def search(args, pkgs):
    """
    package_search:
        search a package using mdapi
        receives argparse arguments and the packages list 
        returns the modified packages list with the available package version
    """
    url = "https://mdapi.fedoraproject.org/"
    branch = args['branch']
    sizes = formater.header()
    for pkg in pkgs:
        pkg_name = pkg['rpm_name']
        req = f"{url}{branch}/pkg/{pkg_name}"
        response = requests.get(req,timeout=30)
        if response.status_code != 200:
            pkg['avaver'] = 'MISS'
            pkg['status'] = 'NOT'
            formater.info(sizes, pkg)
            continue
        data = response.json()
        pkg['avaver'] = data['version']
        pkg = version_compare(pkg)
        if pkg['status'] == 'NOT':
            version = version_define(pkg['minver'])
            pkg_name = add_package_version(pkg['rpm_name'],version)
            req = f"{url}{branch}/pkg/{pkg_name}"
            response = requests.get(req,timeout=30)
            if response.status_code != 200:
                formater.info(sizes,pkg)
                continue
            data = response.json()
            pkg['avaver'] = data['version']
            pkg['rpm_name'] = pkg_name
            pkg = version_compare(pkg)
        time.sleep(1)
        formater.info(sizes, pkg)
    if args['out']:
        with open(args['out'], 'w', encoding="utf-8") as file:
            file.write(json.dumps(pkgs))
    return pkgs

def version_compare(pkg):
    """
    version_compare:
        receive a package and return a package with a status filled
    """
    pkg['status'] = 'NOT'
    pattern = r'^\d+\.\d+\.\d+$'
    if not re.match(pattern, pkg['avaver']):
        return pkg

    if parse_version(pkg['avaver']) != "" and parse_version(pkg['minver']) == "":
        pkg['status'] = 'FOUND'
        return pkg

    if parse_version(pkg['minver']) <= parse_version(pkg['avaver']) < parse_version(pkg['maxver']):
        pkg['status'] = 'FOUND'
    return pkg

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

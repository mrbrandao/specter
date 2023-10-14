#!/usr/bin/env python3
"""
crate:
    manipulate rust crates data
"""

def crate_to_rpm(pkgs):
    """
    crate_to_rpm:
        receives a list of packages and returns a the list appending the
        converted RPM name
        e.g: (crate(foo/default) converts to rust-foo+default-devel
    """
    for pkg in pkgs:
        name = pkg["name"].replace("/",
        "+").strip('()').replace('crate(','rust-')
        pkg['rpm_name'] = f"{name}-devel"
    return pkgs

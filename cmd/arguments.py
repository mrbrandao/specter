#!/usr/bin/env python3
""" 
    arguments:
       defines all the script argpase arguments
"""

import argparse

def flags():
    """
    flags:
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

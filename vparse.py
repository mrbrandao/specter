#!/usr/bin/env python3

import subprocess
import argparse
import re

def run_rpmbuild(input_file):
  cmd = [
      'rpmbuild',
      '-ba',
      input_file
      ]
  result = subprocess.run(cmd, capture_output=True, text=True)
  return result.stderr

#def parse_output(output):
#    pattern = r'([\w-]+)\+(\w+)\sis\sneeded\sby'
#
#    # Use re.search to find the match in the output
#    match = re.search(pattern, output)
#    
#    if match:
#        # Extract the package name and version from the regex groups
#        package_name = match.group(1)
#        version = match.group(2)
#        return package_name, version
#    else:
#        print("No package and version found in the output.")
#        return None, None

def parse_rpmbuild(output,):
    for i in output.split():
      if "-" in i and not "." in i:
        with open(

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-i", 
        "--input", 
        help="Path to the input file"
        )

    args = parser.parse_args()
    output = run_rpmbuild(args.input)
    parse_rpmbuild(output)



    #if output:
    #    package_name, version = parse_output(output)
    #    if package_name and version:
    #        print("Package:", package_name)
    #        print("Version:", version)

if __name__ == "__main__":
    main()

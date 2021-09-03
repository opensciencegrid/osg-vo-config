#!/usr/bin/env python

import glob
import os
import re

regex_dn = re.compile(r"^(/(?:DC|OU|C|ST|L|O)=[^/=]+)*(/CN=([^/=].+))$")

error_log = []

whitelist = [
    'voms-alice-auth.app.cern.ch',
    'voms-atlas-auth.app.cern.ch',
    'voms-cms-auth.app.cern.ch',
    'voms-lhcb-auth.app.cern.ch',
    'voms-ops-auth.app.cern.ch',
]

def validate(dir):
    for file_path in glob.glob(dir + "/*/*.lsc"):
        with open(file_path, 'r') as f:  # reads .lsc files line by line
            lines = f.read().splitlines()

            if check_number_of_dn(lines):
                error_log.append(f'Error in "{file_path}" .lsc file should contain exactly 2 DNs')
            
            subject_cn_value = regex_dn.match(lines[0]).groups()[-1]  # reads subject DN and gets the CN value
            filename_without_ext = os.path.splitext(os.path.basename(file_path))[0]  # extract the file name without extension
            if check_matching_cn(filename_without_ext, subject_cn_value):
                error_log.append(f'Error in "{file_path}" at "{lines[0]}" subject CN value does not match the file name')

            for line in lines:
                if check_format(line):
                    error_log.append(f'Error in "{file_path}" at "{line}" invalid format')

def check_number_of_dn(lines):
    return len(lines) != 2

def check_matching_cn(filename_without_ext, cn_value):
    if filename_without_ext in whitelist:
        return False
    else:
        return filename_without_ext not in cn_value

def check_format(dn):
    return not regex_dn.search(dn)

def print_error_log():
    if error_log:
        for error in error_log:
            print(error)
        error_log.clear()

def main():
    dir = 'vomsdir'
    validate(dir)
    print_error_log()

if __name__ == '__main__':
    main()

#!/usr/bin/python3

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

            if not check_number_of_dn(lines):
                error_log.append(f'Error in "{file_path}" .lsc file should contain exactly 2 DNs')
            
            if not check_matching_cn(lines[0], file_path):
                error_log.append(f'Error in "{file_path}" at "{lines[0]}" subject CN value does not match the file name')

            for bad_line in [line for line in lines if not check_format(line)]:
                error_log.append(f'Error in "{file_path}" at "{bad_line}" invalid format')

def check_number_of_dn(lines):
    return len(lines) == 2

def check_matching_cn(subject_dn, file_path):
    subject_cn_value = regex_dn.search(subject_dn).groups()[-1]  # reads subject DN and gets the CN value
    if subject_cn_value.startswith('host/'):  # remove the 'host/' prefix, if any
        subject_cn_value = subject_cn_value[5:]

    filename_without_ext = os.path.splitext(os.path.basename(file_path))[0]  # extract the file name without extension
    if filename_without_ext in whitelist:
        return True
    else:
        return filename_without_ext == subject_cn_value

def check_format(dn):
    return True if regex_dn.search(dn) else False

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

#!/usr/bin/env python

import os
import re

regex_dn = re.compile(r"^(/(?:DC|OU|C|ST|L|O)=[^/=]+)*(/CN=[^/=].+)$")
regex_subject_cn = re.compile(r"(?<=CN=).*")

error_log = []

def validate(dir):
    for root, subdirs, files in os.walk(dir):
        for file in files:
            if file.endswith('.lsc'):
                file_path = os.path.join(root, file)
                file_name = file[:-len('.lsc')]
                with open(file_path, 'r') as f:  # reads .lsc files line by line
                    lines = f.read().splitlines()
                    if len(lines) != 2:
                        error_log.append("Error in \"" + file_path + "\" .lsc file should contain exactly 2 DNs")
                    subject_cn = regex_subject_cn.search(lines[0]).group()  # reads subject DN and gets the CN
                    for line in lines:
                        match = regex_dn.search(line)
                        if not match:
                            error_log.append("Error in \"" + file_path + "\" at " + line)
                        else:
                            if line == lines[0]:
                                if file_name not in subject_cn:
                                    error_log.append("Error in \"" + file_path + "\" at " + line)
                                continue
                            else:
                                continue

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

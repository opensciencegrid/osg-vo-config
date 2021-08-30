#!/usr/bin/env python

import os
import re

regex = re.compile(r"^(/(?:DC|OU|C|ST|L|O)=[^/=]+)*(/CN=[^/=].+)$")
regexCN = re.compile(r"(?<=CN=).*")

errorLog = []

def validate(dir):
    for root, subdirs, files in os.walk(dir):
        for file in files:
            if file.endswith('.lsc'):
                filePath = os.path.join(root, file)
                fileName = file[:-len('.lsc')]
                with open(filePath, 'r') as f:  # reads .lsc files line by line
                    lines = f.read().splitlines()
                    subjectCN = regexCN.search(lines[0]).group()  # reads subject DN and gets the CN
                    for line in lines:
                        match = regex.search(line)
                        if not match:
                            errorLog.append("Error in \"" + filePath + "\" at " + line)
                        else:
                            if line == lines[0]:
                                if fileName not in subjectCN:
                                    errorLog.append("Error in \"" + filePath + "\" at " + line)
                                continue
                            else:
                                continue

def printErrorLog():
    if errorLog:
        for error in errorLog:
            print(error)
        errorLog.clear()


def main():
    dir = 'vomsdir'
    validate(dir)
    printErrorLog()

if __name__ == '__main__':
    main()
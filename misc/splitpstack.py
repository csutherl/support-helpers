#!/usr/bin/python

import sys

def helpexit():
    print './splitpstack.py <filename>'
    exit(1)
    

if __name__=='__main__':
    if len(sys.argv) != 2:
        helpexit()
    else:
        try:
            currentDate = None
            f = open(sys.argv[1], 'r')
            currentFile = None
            for line in f:
                if 'Date:' in line:
                    currentDate = line.split('Date:')[1].replace(' ', '_')
                    if currentFile:
                        currentFile.close()
                    currentFile = open('pstack-' + currentDate.strip(), 'w')
                if currentDate and currentFile:
                    currentFile.write(line)
        except:
            print 'error!'
        finally:
            f.close()

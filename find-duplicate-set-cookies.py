#!/usr/bin/env python

""" Command to parse access logging and find duplicate JSESSIONID cookies.
Note: The current versions assumes that set-cookie is logged as the last variable in the LogFormat. """

import sys

__author__ = "coty"

filename = sys.argv[1]
print "Reading %s" % filename
with open(filename) as f:
    content = f.readlines()
    IDs = []
    for line in content:
        arr = line.split(' ')
        setCookie = arr[len(arr)-1].strip() + " "
        
        if '-' in setCookie:
            continue

        i = len(arr)-2
        while i > 0:
            if ';' in arr[i]:
                setCookie = arr[i].strip() + " " + setCookie
            else:
                break

            i-=1
        
        JSESSIONID = setCookie[setCookie.find('JSESSIONID'):setCookie.find(';')]
        if len(JSESSIONID) > 0:
            IDs.append(JSESSIONID)

    # Find and print duplicates from the IDs array
    import collections
    dups = [ID for ID, y in collections.Counter(IDs).items() if y > 1]
    if len(dups) > 0:
        print "%s duplicate JSESSIONID(s) found!" % len(dups)
        for dup in dups:
            print dup
    else:
        print "No duplicate JSESSIONIDs found."

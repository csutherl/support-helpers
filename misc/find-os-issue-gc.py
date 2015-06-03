#!/usr/bin/env python

""" Command to parse GC logging and find potential OS issues by checking pause time data. """

import sys
import datetime
import re
import math

import pprint
pp = pprint.PrettyPrinter(indent=4)

__author__ = "coty"

filename = sys.argv[1]

with open(filename) as f:
    content = f.readlines()

    for ns_line in content:
        line = ns_line.strip()
            
        times_match = re.search('\[Times: user=([0-9]+.[0-9]+) sys=([0-9]+.[0-9]+), real=([0-9]+.[0-9]+) secs\]', line)
        if times_match:
            user = float(times_match.group(1))
            sys = float(times_match.group(2))
            total_cpu = user + sys
            real = float(times_match.group(3))

            # checking the difference here and adding a little because of python's silliness with floats
            if (real - total_cpu) > 0.02:
                print "Difference: %s - %s" % ((real - total_cpu), line)

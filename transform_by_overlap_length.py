#!/usr/bin/python

from __future__ import print_function
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


# coverages = open("cov5.txt").read().splitlines()
# overlaps = open("joined_74-204_overlaps.paf").read().splitlines()
overlaps = open("ovlps.paf").read().splitlines()
overlaps = [o.split('\t') for o in overlaps]

for o in overlaps:
  print("{} {} {}".format(
    o[0],
    o[5],
    int((int(o[3]) - int(o[2]) + int(o[8]) - int(o[7])) / 2)
  ))


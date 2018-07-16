#!/usr/bin/python

from __future__ import print_function
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


coverages = open(sys.argv[2]).read().splitlines()
coverages = [c.split(' ') for c in coverages]
coverages = {str(int(c[1]) + 1): int(c[0]) for c in coverages}
overlaps = open(sys.argv[1]).read().splitlines()
overlaps = [o.split('\t') for o in overlaps]

for o in overlaps:
  a_id, b_id = o[0], o[5]
  if a_id in coverages and b_id in coverages:
    print("{} {} {}".format(
      a_id,
      b_id,
      abs(coverages[a_id] - coverages[b_id])
    ))


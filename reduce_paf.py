#!/usr/bin/python3

import sys

remove_indexes = set([])

with open(sys.argv[2]) as f:
  for l in f:
    remove_indexes.add(int(l))

global_index = 0
with open(sys.argv[1]) as f:
  for l in f:
    global_index += 1
    if global_index in remove_indexes:
      continue

    print(l, end='')

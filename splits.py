#!/usr/bin/python3

import sys

count = 0

with open(sys.argv[1]) as f:
  for line in f:
    if line.startswith('@'):
      count += 1

print(count)
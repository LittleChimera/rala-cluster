#!/usr/bin/python3

import sys

global_id = 1

for reads_path in sys.argv[1:]:
  with open(reads_path) as f:
    for line in f:
      if line.startswith('@'):
        print("@{}".format(global_id))
        global_id += 1
      else:
        print(line, end='')
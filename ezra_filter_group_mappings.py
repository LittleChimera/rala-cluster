#!/usr/bin/python3

import sys

group_file = sys.argv[1]
mappings_file = sys.argv[2]
group_id = int(sys.argv[3])

group_reads = set([])

with open(group_file) as f:
  global_group_counter = 0
  for line in f:
    if global_group_counter == group_id:
      group_reads = set(line.split("\t"))
      break
    global_group_counter += 1
# print(group_reads)

with open(mappings_file) as f:
  for line in f:
    # line = line.strip()
    line_comps = line.split("\t")
    if line_comps[0] in group_reads and line_comps[1] in group_reads:
      print(line, end='')


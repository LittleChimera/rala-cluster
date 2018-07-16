#!/usr/bin/python3

import sys

layout_orig = sys.argv[1]
layout_ezra = sys.argv[2]

ctg_seqs_mapping = {}

with open(layout_orig) as f:
  for line in f:
    line = line.strip()
    if line.startswith(">"):
      ctg_seqs_mapping[line[1:line.find(" ")]] = line[line.find('Seqs:') + 5:].split(",")


with open(layout_ezra) as f:
  for line in f:
    line = line.strip()
    contigs = line[1:].split(" ")
    if line.startswith(">"):
      print(">{} Seqs:{}".format(
        ":::".join(contigs),
        ",".join(list(set(sum(
          [ctg_seqs_mapping[c] for c in contigs],
          []
        ))))
      ))
    else:
      print(line)

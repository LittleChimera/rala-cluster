#!/usr/bin/python3

import csv
import sys
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from overlap import *
from random import randint
import numpy as np


ylim_high = 1000
plt.figure(figsize=(9, 90))
plt.ylim([0,ylim_high])


overlaps_file = sys.argv[1]
coverages_file = sys.argv[2]
# layout_file = sys.argv[3]

overlaps = {}
coverages = {}
ignored_dots = 0
dots = []

with open(coverages_file) as f:
  for line in f:
    line = line.split(' ')
    coverages[int(line[1])] = int(line[0])

print("read coverages")

split = 91816

with open(overlaps_file) as f:
  for line in f:
    line = line.split("\t")
    a = int(line[0])
    av = (int(line[3]) - int(line[2])) * 100.0 / int(line[1])
    b = int(line[5])
    bv = (int(line[8]) - int(line[7])) * 100.0 / int(line[6])

    if coverages[a] == 0 or coverages[b] == 0:
      ignored_dots += 1
      continue

    if (a <= split) == (b <= split):
      continue

    plt.plot(
      (int(line[3]) - int(line[2])) * 100.0 / int(line[1]),
      abs(coverages[a] - coverages[b]) * 100.0 / coverages[a],
      'g.', markersize=2
    )
    plt.plot(
      (int(line[8]) - int(line[7])) * 100.0 / int(line[6]),
      abs(coverages[b] - coverages[a]) * 100.0 / coverages[b],
      'g.', markersize=2
    )

print("read overlaps")

# with open(layout_file) as f:
#   for line in f:
#     if line.startswith('>'):
#       reads = [int(id) for id in line[line.find("Seqs") + 5:].split(",")]
#       for read_a, read_b in zip(reads, reads[1:]):
#         olp_av, olp_bv = overlaps[(min(read_a, read_b) + 1, max(read_a, read_b) + 1)]

#         if coverages[read_a] != 0 and coverages[read_b] != 0:
#           dot_a = (
#             olp_av, abs(coverages[read_a] - coverages[read_b]) * 100.0 / coverages[read_a], 'r' if olp_av > olp_bv else 'b'
#           )
#           dot_b = (
#             olp_bv, abs(coverages[read_b] - coverages[read_a]) * 100.0 / coverages[read_b], 'r' if olp_bv > olp_av else 'b'
#           )
#           if dot_a[1] > 1000.0 or dot_b[1] > 1000.0:
#             ignored_dots += 2
#             continue

#           dots.append(dot_a)
#           dots.append(dot_b)

##
# plot_dots = [list(t) for t in zip(*dots)]
# plot_dots = dots
# with open("plot_{}-dots.py".format(sys.argv[4]), "w") as f:
#   print(plot_dots, file=f)


plt.yticks(np.arange(0,ylim_high,10))
plt.savefig("plot_{}.png".format(sys.argv[4]))

if ignored_dots > 0:
  print("{} / {} ~ {}%".format(
    ignored_dots,
    ignored_dots + len(dots),
    ignored_dots * 100.0 / (ignored_dots + len(dots))
  ))
else:
  print("No ignored dots")
# plt.show()

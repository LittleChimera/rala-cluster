#!/usr/bin/python3

import csv
import sys
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import os

values = []

with open(sys.argv[1]) as csvfile:
  spamreader = csv.reader(csvfile, delimiter=' ')
  for row in spamreader:
    # coverage, read_id, ref_id
    values.append((int(row[-2]), int(row[0]), int(row[-1])))

histogram = [0] * (max([m for m, _, _ in values]) + 1)
ref1 = histogram[:]
ref2 = histogram[:]
for m, i, ref in values:
  if ref == 0:
    ref1[m] += 1
  if ref == 1:
    ref2[m] += 1
  histogram[m] += 1

plt.figure(figsize=(15, 15))
plt.bar(range(0, len(histogram)), histogram)
plt.bar(range(0, len(histogram)), ref1)
plt.bar(range(0, len(histogram)), ref2)
plt.savefig("histogram_{}.png".format(
  os.path.splitext(os.path.basename(sys.argv[1]))[0]
))
# plt.show()

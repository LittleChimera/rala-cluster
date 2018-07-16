#!/usr/bin/python

from __future__ import print_function
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

reads_info_file = sys.argv[1]
mcl_out = sys.argv[2]

reads = open(reads_info_file).read().splitlines()
reads = [c.split(' ') for c in reads]
reads = {str(int(c[0])): int(c[-1]) for c in reads}
clusters = open(mcl_out).read().splitlines()
clusters = [c.split('\t') for c in clusters]

total_missed = 0

for c in clusters:
  real_clustering = [reads[r] if r in reads else 2 for r in c]
  a_count = real_clustering.count(0)
  b_count = real_clustering.count(1)
  c_count = real_clustering.count(2)
  if a_count != 0 and b_count != 0:
    total_missed += min(a_count, b_count)
  print("{:.4f},{},{},{}".format(float(max(a_count, b_count)) / len(c), a_count, b_count, c_count))

print(",")
print("Total missed,{}".format(total_missed))
print("Clusters total,{}".format(len(clusters)))
print(",")

def info_by_size(size):
  print("Clusters,{:6d},{:6d},{:8d}".format(
    size,
    sum([1 if len(c) > size else 0 for c in clusters]),
    sum([len(c) if len(c) > size else 0 for c in clusters])
  ))

info_by_size(0)
info_by_size(100)
info_by_size(1000)
info_by_size(10000)


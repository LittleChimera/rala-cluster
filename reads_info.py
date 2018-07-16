#!/usr/bin/python3

from __future__ import print_function
import sys
import statistics, getopt
from multiprocessing.dummy import Pool
from overlap import *

def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

def help():
  print(
  "usage: ./median.py [arguments ...]\n"
  "arguments:\n"
  "    --data\n"
  "        (required)\n"
  "        TODO\n"
  "    --splits TODO\n"
  "        TODO\n"
  "    --quantil TODO\n"
  "        TODO\n"
  "    -h, --help\n"
  "    prints out the help")

options = "h"
long_options = ["help", "data=", "splits=", "quantil="]

try:
  opts, args = getopt.getopt(sys.argv[1:], options, long_options)
except getopt.GetoptError as err:
  print(str(err))
  help()
  sys.exit()

splits = []
overlaps_file = None
quantil = 0

for option, argument in opts:
  if option == "--splits":
    splits = list(map(int, argument.split(",")))
  if option == "--quantil":
    quantil = float(argument)
  elif option == "--data":
    overlaps_file = argument
  elif option in ("-h", "--help"):
    help()
    sys.exit()

def ref_id(read):
  total = 0
  id = -1
  for s in splits:
    if total > read:
      break
    else:
      id += 1
      total += s
  return id

coverages = {}
overlaps_starts = {}
overlaps_ends = {}
overlap_count = {}

def init_overlap(overlap):
  if overlap.target not in coverages:
    coverages[overlap.target] = [0 for _ in range(overlap.target_length)]
    overlaps_starts[overlap.target] = {}
    overlaps_ends[overlap.target] = {}
    overlap_count[overlap.target] = {'left': 0, 'right': 0, 'other': 0}

def prep_coverage(overlap):
  if overlap.start in overlaps_starts[overlap.target]:
    overlaps_starts[overlap.target][overlap.start] += 1
  else:
    overlaps_starts[overlap.target][overlap.start] = 1

  if overlap.end in overlaps_ends[overlap.target]:
    overlaps_ends[overlap.target][overlap.end] += 1
  else:
    overlaps_ends[overlap.target][overlap.end] = 1


def overlap_side(overlap_a, overlap_b, strand):
  leftover_query_left = overlap_a.start
  leftover_query_right = overlap_a.target_length - overlap_a.end
  if not strand:
    leftover_query_left, leftover_query_right = leftover_query_right, leftover_query_left

  leftover_target_left = overlap_b.start
  leftover_target_right = overlap_b.target_length - overlap_b.end

  if leftover_query_left > leftover_target_left and leftover_query_right < leftover_target_right:
    return 0
  elif leftover_query_left < leftover_target_left and leftover_query_right > leftover_target_right:
    return 1
  else:
    return -1

with open(overlaps_file) as f:
  for line in f:
    line = line.split('\t')
    overlap_a = parse_overlap(line[:4])
    overlap_b = parse_overlap(line[5:9])
    init_overlap(overlap_a)
    init_overlap(overlap_b)
    prep_coverage(overlap_a)
    prep_coverage(overlap_b)

    side = overlap_side(overlap_a, overlap_b, line[4] == '+')
    if side > 0:
      overlap_count[overlap_a.target]['right' if overlap_side == 0 else 'left'] += 1
      overlap_count[overlap_b.target]['right' if overlap_side == 1 else 'left'] += 1
    else:
      overlap_count[overlap_a.target]['other'] += 1
      overlap_count[overlap_b.target]['other'] += 1


eprint("File read")

def fill_coverage(read, coverage):
  coverage_increment = 0
  for i in range(len(coverage)):
    if i in overlaps_starts[read]:
      coverage_increment += overlaps_starts[read][i]
    if i in overlaps_ends[read]:
      coverage_increment -= overlaps_ends[read][i]
    coverage[i] = coverage_increment

pool = Pool()
pool.starmap(fill_coverage, coverages.items())

def find_local_coverage(coverage):
  best_coverage_start, best_coverage_end = None, None
  local_coverage_start = None
  for ci in range(len(coverage)):
    if coverage[ci] >= 3 and local_coverage_start is None:
      local_coverage_start = ci

    if local_coverage_start is not None and (coverage[ci] < 3 or ci == len(coverage) - 1):
      if best_coverage_start is None or best_coverage_end - best_coverage_start < ci - local_coverage_start:
        best_coverage_start, best_coverage_end = local_coverage_start, ci
      local_coverage_start = None

  return coverage[best_coverage_start:best_coverage_end] if best_coverage_start else coverage


for read, coverage in coverages.items():
  ref = ref_id(int(read))
  read_length = len(coverage)
  if sorted(coverage)[int(read_length*50/100)] < 3:
    coverage = find_local_coverage(coverage)
    read_length = len(coverage)

  coverage = sorted(coverage)

  print(" ".join([ str(x) for x in [
    read,
    # coverage[int(read_length*5/100)],
    coverage[int(read_length*10/100)],
    # coverage[int(read_length*25/100)],
    coverage[int(read_length*50/100)],
    coverage[int(read_length*90/100)],
    # coverage[int(read_length*90/100)] - coverage[int(read_length*10/100)],
    overlap_count[read]['left'],
    overlap_count[read]['right'],
    overlap_count[read]['other'],
    # abs(overlap_count[read]['left'] - overlap_count[read]['right']),
    ref
  ]]))
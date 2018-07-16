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
  "    --split TODO\n"
  "        TODO\n"
  "    --quantil TODO\n"
  "        TODO\n"
  "    -h, --help\n"
  "    prints out the help")

options = "h"
long_options = ["help", "data=", "split=", "quantil="]

try:
  opts, args = getopt.getopt(sys.argv[1:], options, long_options)
except getopt.GetoptError as err:
  print(str(err))
  help()
  sys.exit()

split = 0
overlaps_file = None
quantil = 0

for option, argument in opts:
  if option == "--split":
    split = int(argument)
  if option == "--quantil":
    quantil = float(argument)
  elif option == "--data":
    overlaps_file = argument
  elif option in ("-h", "--help"):
    help()
    sys.exit()

coverages = {}
overlaps_starts = {}
overlaps_ends = {}

def init_overlap(overlap):
  if overlap.target not in coverages:
    coverages[overlap.target] = [0 for _ in range(overlap.target_length)]
    overlaps_starts[overlap.target] = {}
    overlaps_ends[overlap.target] = {}

def prep_coverage(overlap):
  if overlap.start in overlaps_starts[overlap.target]:
    overlaps_starts[overlap.target][overlap.start] += 1
  else:
    overlaps_starts[overlap.target][overlap.start] = 1

  if overlap.end in overlaps_ends[overlap.target]:
    overlaps_ends[overlap.target][overlap.end] += 1
  else:
    overlaps_ends[overlap.target][overlap.end] = 1

with open(overlaps_file) as f:
  for line in f:
    line = line.split('\t')
    overlap_a = parse_overlap(line[:4])
    overlap_b = parse_overlap(line[5:9])
    init_overlap(overlap_a)
    init_overlap(overlap_b)
    prep_coverage(overlap_a)
    prep_coverage(overlap_b)

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

for read, coverage in coverages.items():
  ref = 0 if int(read) <= split else 1
  read_length = len(coverage)
  cutoff = int(read_length * quantil)
  print("{} {} {}".format(int(statistics.median(set(coverage[(cutoff):(read_length - cutoff)]))), read, ref))
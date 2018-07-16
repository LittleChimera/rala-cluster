#!/usr/bin/python3

from __future__ import print_function, division
import sys
from overlap import *
import numpy as np

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


info = open(sys.argv[2]).read().splitlines()
info = [i.split(' ') for i in info]
info = {str(int(c[0])): list(map(int, c[1:-1])) for c in info}
overlaps = open(sys.argv[1]).read().splitlines()
overlaps = [o.split('\t') for o in overlaps]

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

for o in overlaps:
  a_id, b_id = o[0], o[5]
  if a_id in info and b_id in info:
    overlap_a = parse_overlap(o[:4])
    overlap_b = parse_overlap(o[5:9])
    side = overlap_side(overlap_a, overlap_b, o[4] == '+')
    # if side == -1:
    #   continue
    print("{} {} {}".format(
      a_id,
      b_id,
      # abs(info[a_id][0] - info[b_id][0])

      # # winning
      np.median([
        abs(info[a_id][0] - info[b_id][0]) / max(info[a_id][0], info[b_id][0], 1),
        max(
          abs(info[a_id][2] - info[b_id][1]) / max(abs(info[a_id][2]), abs(info[b_id][1]), 1),
          abs(info[b_id][2] - info[a_id][1]) / max(abs(info[b_id][2]), abs(info[a_id][1]), 1)
        )] + ([
        abs(
          (info[a_id][4] - info[b_id][3]) / max(abs(info[a_id][4]), abs(info[b_id][3]), 1) if side == 0 else \
          (info[a_id][3] - info[b_id][4]) / max(abs(info[a_id][3]), abs(info[b_id][4]), 1)
        )] if side != -1 else [])
      ) #* ((int(o[10]) / int(o[9])) ** 1)


      # max(
      #   abs(info[a_id][0] - info[b_id][0]),
      #   max(
      #     abs(info[a_id][2] - info[b_id][1]),
      #     abs(info[b_id][2] - info[a_id][1])
      #   ),
      #   abs(
      #     info[a_id][4] - info[b_id][3] if side == 0 else info[a_id][3] - info[b_id][4]
      #   )
      # ) * ((int(o[10]) / int(o[9])) ** 2)
    ))


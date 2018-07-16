#!/usr/bin/python3

from __future__ import print_function
import sys
import numpy as np

def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

overlaps = []
length = None

with open(sys.argv[1]) as f:
  for line in f:
    line = line.strip().split("\t")
    if length is None:
      length = int(line[1])
    start = int(line[2])
    end = int(line[3])
    query = line[5]
    overlaps.append((
      end - start, start, end, query
    ))

contig_purities = {}
with open(sys.argv[2]) as f:
  for line in f:
    line = line.split(",")
    contig_purities[line[0]] = float(line[1])

if length is None:
  print("Cover,N/A")
  # print("NG50,N/A")
  print("NG{},{}".format(50, 'N/A'))
  print("NG{} median purity,{}",format(50, 'N/A'))
  print("NG{} low purity,{}",format(50, 'N/A'))
  print("NG{},{}".format(90, 'N/A'))
  print("NG{} median purity,{}",format(90, 'N/A'))
  print("NG{} low purity,{}",format(90, 'N/A'))
  sys.exit(0)


overlaps = sorted(overlaps, reverse=True)

covers = []
def calc_cov_len():
  return sum([c[0] for c in covers])

def cover_overlap(cover, overlap):
  if overlap[1] >= cover[1] and overlap[2] <= cover[2]:
    return None

  if overlap[2] <= cover[1] or overlap[1] >= cover[2]:
    return overlap

  if overlap[1] < cover[1]:
    return ((
      cover[1] - overlap[1], overlap[1], cover[1], overlap[3]
    ))

  if overlap[2] > cover[2]:
    return ((
      overlap[2] - cover[2], cover[2], overlap[2], overlap[3]
    ))

  raise Exception("This shoudln't be a valid case...")

covering_overlaps = overlaps[:]
used_queries = []
cov_length = 0
cov_percent = 0.0

while covering_overlaps != []:
  # for co in covering_overlaps:
  #   print("{} - {}".format(co[0], co[3]))
  ol = covering_overlaps[0]
  covering_overlaps = covering_overlaps[1:]

  # if ol[3] in used_queries:
  #   continue
  # else:
  #   used_queries.append(ol[3])

  ol_parts = [ol[:]]

  cov_length = calc_cov_len()
  cov_percent = cov_length / float(length) * 100
  # eprint("Cover: {:2f}%, {}".format(cov_percent, cov_length))

  # if cov_percent >= 95:
  #   break
  for cov in covers:
    ol_parts = [cover_overlap(cov, olp) for olp in ol_parts]
    ol_parts = [olp for olp in ol_parts if olp is not None]
  for olp in ol_parts:
    if olp:
      covers.append(olp)

  for cov in covers:
    covering_overlaps = [cover_overlap(cov, olp) for olp in covering_overlaps]
    covering_overlaps = [olp for olp in covering_overlaps if olp is not None]
  covering_overlaps = sorted(covering_overlaps, reverse=True)


eprint("Total overlaps: {}".format(len(overlaps)))
eprint("Total covers: {}".format(len(set([c[3] for c in covers]))))

print("Cover,{:2f}%,{} / {}".format(cov_percent, cov_length, length))

def ng_score(score):
  ngcov = 0
  ng_ctgs = []
  for c in sorted(covers, reverse=True):
    if c[3] not in ng_ctgs:
      ng_ctgs.append(c[3])

    ngcov += c[0]
    if ngcov / float(length) >= score / 100.0:
      break

  ng_ctgs_purities = [contig_purities[ctg] for ctg in ng_ctgs]

  print("NG{},{}".format(score, len(ng_ctgs) if ngcov / float(length) >= score / 100.0 else "N/A"))
  print("NG{} median purity,{}".format(score, np.median(ng_ctgs_purities)))
  print("NG{} low purity,{}".format(score, min(ng_ctgs_purities)))

ng_score(50)
ng_score(90)
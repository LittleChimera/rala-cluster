#!/usr/bin/python3

from __future__ import print_function
import numpy as np
import sys
from queue import Queue
# from threading import Thread
import multiprocessing
# from scipy.spatial import distance
import logging
from multiprocessing.dummy import Pool as ThreadPool
from overlap import *

PRECISION = 3

log = None
logging.basicConfig(level=logging.DEBUG)
np.set_printoptions(precision=PRECISION)

clustering_file = sys.argv[1]
overlaps_file = sys.argv[2]
coverages_file = sys.argv[3]
improving_iterations = int(sys.argv[4]) if len(sys.argv) >= 5 else 10

overlaps = {}
cluster_mapping = {}
coverages = {}
cluster_count = 0
read_count = 0

def fill_overlaps(a, b):
  if a.target not in overlaps:
    overlaps[a.target] = [b]
  else:
    overlaps[a.target].append(b)

with open(overlaps_file) as f:
  for line in f:
    overlap_a, overlap_b = parse_paf_line(line)
    fill_overlaps(overlap_a, overlap_b)
    fill_overlaps(overlap_b, overlap_a)

with open(clustering_file) as f:
  cluster_index = 0
  for line in f:
    for read in line.split('\t'):
      read_count = max(int(read), read_count)
      cluster_mapping[int(read)] = cluster_index
    cluster_index += 1
  cluster_count = cluster_index

# with open(coverages_file) as f:
#   for line in f:
#     line = line.split(' ')
#     coverages[line[1]] = (int(line[0]), int(line[2]))

def improve_clusters(log=False):
  logging.info("Flooding...")

  visited = {i: False for i in range(1, read_count + 1)}
  subc = {}
  subc_values = {}
  subc_current = 1
  subc_current_value = 0
  q = Queue()

  for i in range(1, read_count + 1):
    if visited[i]:
      continue

    # logging.info("Flooding {}...".format(i))
    q.put(i)
    visited[i] = True

    while not q.empty():
      node = q.get()
      if node not in overlaps:
        continue

      subc[node] = subc_current
      subc_current_value += 1
      for j in overlaps[node]:
        if j.target in cluster_mapping and \
          node in cluster_mapping and \
          not visited[j.target] and \
          cluster_mapping[node] == cluster_mapping[j.target]:
          # do stuff
          visited[j.target] = True
          q.put(j.target)

    subc_values[subc_current] = subc_current_value
    subc_current += 1
    subc_current_value = 0
  # logging.info(subc_values)

  logging.info("Calculating p...")

  p = np.zeros((read_count + 1, cluster_count))
  pool = ThreadPool(multiprocessing.cpu_count())
  def adjust_pi(i):
    adjust_p(p, subc_values, subc, i)

  pool.map(adjust_pi, range(1, read_count + 1))


def adjust_p(p, subc_values, subc, i):
  if i not in cluster_mapping or \
    i not in overlaps:
    return
  for j in range(int(len(overlaps[i]))):
    if overlaps[i][j].target not in cluster_mapping or\
      j not in subc:
      continue
    #median_diff = 1. / (abs(X[i] - X[j]) + 1)
    p[i][cluster_mapping[overlaps[i][j].target]] += subc_values[subc[j]] #* median_diff
  best_cluster = move_single_read(cluster_mapping[i], p[i], i)
  if best_cluster is not None:
    cluster_mapping[i] = best_cluster

def move_single_read(ci, pi, i):
  if len(overlaps[i]) == 0:
    return None
  return np.argmax(pi)

for i in range(improving_iterations):
  logging.info('---> Iteration: {}'.format(i))
  improve_clusters()

for i in range(cluster_count):
  for read, cluster_index in cluster_mapping.items():
    if cluster_index == i:
      print(read, end='\t')
  print('\n', end='')

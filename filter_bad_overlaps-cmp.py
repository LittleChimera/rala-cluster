#!/usr/bin/python3
from __future__ import print_function

def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

from time import time

import numpy as np
import sys
from overlap import *
import math

import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn import manifold, datasets
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import normalize


data_file = sys.argv[1]
overlaps_file = sys.argv[2]
X, y = [], []

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

def quartile_diffs_ratio(data, a, b, i, j):
    a_diff = data[a][2] - data[a][1]
    b_diff = data[b][2] - data[b][1]
    if a_diff == 0:
        a_diff += 1
    if b_diff == 0:
        b_diff += 1

    if a_diff > b_diff:
        return a_diff / b_diff
    else:
        return b_diff / a_diff

def quartile_diffs(data, a, b, i, j):
    return (
        abs(data[a][i] - data[b][j]),
        abs(data[a][j] - data[b][i])
    )


split = 91816

data = {}
skipped = 0
invalid_skipped = 0
skipped_indexes = []
global_overlap_index = -1
y_overlap_index_mapping = []
with open(data_file) as f:
  for line in f:
    d = [int(x) for x in line.split(" ")]
    data[d[0]] = np.array(d[1:-1])

with open(overlaps_file) as f:
  for line in f:
    global_overlap_index += 1
    line = line.split("\t")
    a, b = int(line[0]), int(line[5])
    overlap_a = parse_overlap(line[:4])
    overlap_b = parse_overlap(line[5:9])
    side = overlap_side(overlap_a, overlap_b, line[4] == '+')
    if side == -1:
        skipped += 1
        skipped_indexes.append(global_overlap_index)
        invalid_skipped += (1 if (a <= split) != (b <= split) else 0)
        continue

    x = []
    x.append(int(line[9]) / int(line[10]))
    x.append(abs(data[a][0] - data[b][0]))  # 10-perc
    x.append(abs(data[a][1] - data[b][1]))  # 50-perc
    x.append(abs(data[a][2] - data[b][2]))  # 90-perc

    x.append(quartile_diffs_ratio(data, a, b, 0, 1))
    x.append(quartile_diffs_ratio(data, a, b, 0, 2))
    x.append(quartile_diffs_ratio(data, a, b, 1, 2))

    x.append(max(quartile_diffs(data, a, b, 0, 1)))  # max a-b 50-10-perc diff
    x.append(max(quartile_diffs(data, a, b, 0, 2)))  # max a-b 90-10-perc diff
    x.append(max(quartile_diffs(data, a, b, 1, 2)))  # max a-b 90-50-perc diff

    x.append(min(quartile_diffs(data, a, b, 0, 1)))  # min a-b 50-10-perc diff
    x.append(min(quartile_diffs(data, a, b, 0, 2)))  # min a-b 90-10-perc diff
    x.append(min(quartile_diffs(data, a, b, 1, 2)))  # min a-b 90-50-perc diff

    x.append(abs(
        data[a][4] - data[b][3] if side == 0 else data[a][3] - data[b][4]
    ))

    X.append(x)
    y.append(1 if (a <= split) != (b <= split) else 0)
    y_overlap_index_mapping.append(global_overlap_index)

X = np.array(X)

X_train, X_check, y_train, y_check = train_test_split(
    X, y, test_size=0.9, random_state=11)

# X_train = normalize(X_train)
# X_check = normalize(X_check)
#_, X_check, _, y_check = train_test_split(
#    X, y, test_size=0.01, random_state=42)
# X_check = X
# y_check = y
print("Examples taken to build: {}".format(y_train.count(1)))

clfs = []
clfs.append(SVC(kernel='rbf'))
clfs.append(sklearn.ensemble.RandomForestClassifier(n_estimators=500))
clfs.append(GaussianNB())

for clf in clfs:

    print("starting classification")
    clf.fit(X_train, y_train)
    print("scoring")
    y_pred = clf.predict(X_check)
    print(sklearn.metrics.precision_score(y_check, y_pred))
    print(sklearn.metrics.recall_score(y_check, y_pred))
    print(sklearn.metrics.accuracy_score(y_check, y_pred))
    removed_overlaps = 0
    removed_invalid_overlaps = 0
    kept_invalid_overlaps = 0
    for i in range(len(y_check)):
        if y_pred[i] == 0 and y_check[i] == 1:
            kept_invalid_overlaps += 1
        if y_pred[i] == 1:
            removed_overlaps += 1
            if y_pred[i] == y_check[i]:
                removed_invalid_overlaps += 1

    print(removed_invalid_overlaps, removed_overlaps, kept_invalid_overlaps)
    print(skipped, invalid_skipped)


#!/usr/bin/python3

import os
import sys

result_files = [ sys.argv[1] + '/' + f for f in os.listdir(sys.argv[1]) if f.find('.err') != -1 ]

result = {}

for file in result_files:
  column = file.split('_')[1]
  if column not in result:
    result[column] = {}
  row = '_'.join(file.split('_')[2:5]).split('.')[0]
  with open(file) as f:
    content = f.read()
    total_missed = content.split('\n')[0].split(':')[1].strip()
    total = content.split('\n')[2].split('|')[1].strip()
    result[column][row] = "{:.2f}%, {} / {}".format(float(total_missed) / int(total) * 100, total_missed, total)

def cmp_column_keys(x, y):
  x_a = x.split('-')[0]
  x_b = x.split('-')[1]
  y_a = y.split('-')[0]
  y_b = y.split('-')[1]

  if x_a == y_a:
    return x_b - y_b
  else:
    return x_a - y_a

columns = sorted(result.keys(), key=lambda x: (int(x.split('-')[0]), int(x.split('-')[1])))
print(',,'.join([''] + columns))
for row in sorted(result[columns[1]].keys(), key=lambda x: (int(x.split('_')[2]), x.split('_')[0])):
  print(','.join([row] + [result[col][row] for col in columns]))
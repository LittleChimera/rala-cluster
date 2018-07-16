#!/usr/bin/python3
import sys
import numpy as np

# split = [91816,151180,344403,0]
# ref_ids = [74, 235, 1080, 2218]
split = [int(split) for split in sys.argv[1].split(",")] + [0]
ref_ids = [int(ref_id) for ref_id in sys.argv[2].split(",")]
layout_file = sys.argv[3]
reads_file = sys.argv[4]

def ref_id(read):
  total = 0
  id = -1
  for s in split:
    if total > read:
      break
    else:
      id += 1
      total += s
  return ref_ids[id]

print(",".join(
  ["Status"] +
  ["Ref {}".format(str(id)) for id in ref_ids] +
  ["Contig length"]
))

read_lengths = {}
with open(reads_file) as f:
  read_id = None
  for l in f:
    if l.startswith("@"):
      read_id = int(l[1:])
    elif read_id is not None:
      read_lengths[read_id] = len(l)
      read_id = None

purities = []
total_contaminated_length = 0
with open(layout_file) as f:
  contig_summary = {}
  for line in f:
    if line.startswith('>'):
      reads = [int(id) + 1 for id in line[line.find("Seqs") + 5:].split(",")]
      refs = [ref_id(read) for read in reads]

      summary = {id: 0 for id in ref_ids}
      contig_ref_lengths = {id: 0 for id in ref_ids}
      for read, ref in zip(reads, refs):
        summary[ref] += 1
        contig_ref_lengths[ref] += read_lengths[read]

      total_contaminated_length += sum(sorted(contig_ref_lengths.values(), reverse=True)[1:])
      purities.append(sorted(contig_ref_lengths.values(), reverse=True)[0] / sum(contig_ref_lengths.values()) * 100.0)
      contig_summary = summary
    else:
      # print(contig_summary)0

      print(','.join(
        ["MIXED" if list(contig_summary.values()).count(0) != len(ref_ids) - 1 else ""] +
        [str(contig_summary[id]) for id in ref_ids] +
        [str(len(line))]
      ))
      # print("{:10d}  {}".format(len(line), contig_summary))
print(",")
print("Mean purity,{}".format(np.mean(purities)))
print("Mean purity (mixed),{}".format(np.mean([p for p in purities if p < 100.0])))
print("Low purity,{}".format(sorted(purities)[0]))
print("Mixed count,{}".format(len(purities) - purities.count(100.0)))
print("Total contaminated length,{}".format(total_contaminated_length))
print(",")
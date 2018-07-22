#!/usr/bin/python3

from __future__ import print_function
import sys, os, subprocess, shutil

def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

rala_path = "./vendor/rala/bin/rala"

sequence_path = sys.argv[1]
overlaps_path = sys.argv[2]
mcl_path = sys.argv[3]

min_cluster_size = 1000

out_dir = "./.working_directory/ra/rala_out_pipeline/joined-{}".format(os.path.basename(os.path.splitext(sequence_path)[0]).split("_")[2])
if os.path.exists(out_dir):
  shutil.rmtree(out_dir)
os.makedirs(out_dir)

def run_rala(group_id):
  eprint('[Ra::run] run: Running for group {}...'.format(group_id))
  rala_params = [rala_path, '-t', "24", "-m", str(group_id)]
  rala_params.extend([sequence_path, overlaps_path, mcl_path])

  layout = os.path.join(os.getcwd(), "{}/layout_{}.fasta".format(
    out_dir, group_id
  ))
  try:
    layout_file = open(layout, "w")
  except OSError:
    eprint('[Ra::run] error: unable to create layout file!')
    sys.exit(1)

  try:
    print(" ".join(rala_params))
    p = subprocess.Popen(rala_params, stdout=layout_file)
  except OSError:
    eprint('[Ra::run] error: unable to run rala!')
    sys.exit(1)
  p.communicate()
  if (p.returncode != 0):
    sys.exit(1)

  layout_file.close()


with open(mcl_path) as mcl_out:
  group_id = 0
  for line in mcl_out:
    if len(line.split("\t")) > min_cluster_size:
      run_rala(group_id)
    group_id += 1

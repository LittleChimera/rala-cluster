#!/usr/bin/python3
from __future__ import print_function
import sys, os, subprocess, multiprocessing, glob, re

def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

version = "ezra"

threads = str(multiprocessing.cpu_count())

# input data directory
single_sequence_dir = sys.argv[1]

sequences_dir = './.working_directory/joined_data'
overlaps_dir = './.working_directory/overlaps'
reads_info_dir = './.working_directory/reads_info'
overlaps_dir = './.working_directory/overlaps'
mcl_input_dir = './.working_directory/mcl/input'
mcl_output_dir = './.working_directory/mcl/output'
rala_out_dir = './.working_directory/ra/rala_out_pipeline'
splits_dir = './.working_directory/splits'
filtered_overlaps_dir = './.working_directory/filtered_overlaps'

reduce_paf_exec = './reduce_paf.py'
filter_bad_ovlps_exec = './filter_bad_overlaps.py'
splits_exec = './splits.py'
reads_info_exec = './reads_info.py'
join_reads_exec = './join_reads.py'
rala_stat_exec = './rala_stat.py'
contig_purities_exec = './contig_purities.py'
ovlp_stat_exec = './stats_ovlp.py'
transform_mcl_input_exec = './transform_info.py'
cluster_results_exec = './cluster_results.py'
mcl_exec = './vendor/mcl/src/shmcl/mcl'
sra_exec = './sra.py'
minimap2_exec = './vendor/minimap2/minimap2'
ezra_exec = './vendor/ezra/ezra'
ezra_minimap_reduce_exec = './ezra_filter_group_mappings.py'
ezra_adjust_layout_exec = './ezra_adjust_ctg_values.py'

mcl_granularity = "1.12"

ref_ids = sys.argv[2:]
ref_ids_str = "-".join(ref_ids)

filtered_overlaps_file = os.path.join(overlaps_dir, "fbo_{}.out".format(ref_ids_str))
ref_files = [os.path.join(single_sequence_dir, "NCTC{}_ref.fasta".format(id)) for id in ref_ids]
ref_sequences_files = [os.path.join(single_sequence_dir, "NCTC{}_formatted_reads.fastq".format(id)) for id in ref_ids]
sequences_file = os.path.join(sequences_dir, "joined_reads_{}.fastq".format(ref_ids_str))
overlaps_file = os.path.join(overlaps_dir, "overlaps_{}_pb.paf".format(ref_ids_str))
reduced_overlaps_file = os.path.join(overlaps_dir, "reduced_overlaps_{}_pb.paf".format(ref_ids_str))
reads_info_file = os.path.join(reads_info_dir, "reads_info_{}.out".format(ref_ids_str))
mcl_input_file = os.path.join(mcl_input_dir, "graph_reduced_{}_v{}_pb.in".format(ref_ids_str, version))
mcl_out_file = os.path.join(mcl_output_dir, "graph_{}_pb_v{}_{}.out".format(ref_ids_str, version, mcl_granularity.replace('.', '_')))
layout_out_dir = os.path.join(rala_out_dir, "joined-{}".format(ref_ids_str))
layout_glob = str(os.path.join(layout_out_dir, "layout_".format(ref_ids_str))) + "*.fasta"
ezra_layout_glob = str(os.path.join(layout_out_dir, "ezra_layout_".format(ref_ids_str))) + "*.fasta"
stat_out_file = os.path.join(layout_out_dir, "stat.csv")
stat_out_summary_file = os.path.join(layout_out_dir, "stat-summary.csv")
cluster_results_file = os.path.join(layout_out_dir, "cluster_results.csv")

if not os.path.exists('./.working_directory'):
  os.makedirs('./.working_directory')

def run_step(args, out=None, err=None):
  print(args)
  print(out, err)
  if out != None and os.path.isfile(out):
    eprint('Results already exist for stdout={}'.format(out))
    return

  if type(out) is str:
    out_dir = os.path.dirname(out)
    if not os.path.exists(out_dir):
      os.makedirs(out_dir)
    out = open(out, 'w')
  if type(err) is str:
    err_dir = os.path.dirname(err)
    if not os.path.exists(err_dir):
      os.makedirs(err_dir)
    err = open(err, 'w')
  try:
    p = subprocess.Popen(args, stdout=out, stderr=err)
  except OSError as e:
    eprint('Failed running {}\n to stdout={}\tstderr={}\n{}'.format(args, out, err, e))
    sys.exit(1)
  pout, perr = p.communicate()
  if (p.returncode != 0):
    sys.exit(1)

  try:
    out.close()
  except Exception:
    pass
  try:
    err.close()
  except Exception:
    pass

  if pout is not None:
    pout = pout.decode('UTF-8')
  if perr is not None:
    perr = perr.decode('UTF-8')

  return pout, perr

for ref_id, ref_file in zip(ref_ids, ref_sequences_files):
  run_step([
    splits_exec,
    ref_file
  ], out=os.path.join(splits_dir, "split-{}.out".format(ref_id)))

splits = []
for id in ref_ids:
  with open(os.path.join(splits_dir, "split-{}.out".format(id)), 'r') as f:
    splits.append(f.read().strip())

run_step([
  join_reads_exec,
  *ref_sequences_files
], out=sequences_file)

run_step([
  minimap2_exec,
  '-t',
  threads,
  '-x',
  'ava-pb',
  sequences_file,
  sequences_file
], out=overlaps_file)

run_step([
  reads_info_exec,
  '--data',
  overlaps_file,
  '--split',
  ",".join(splits)
], out=reads_info_file)

run_step([
  filter_bad_ovlps_exec,
  reads_info_file,
  overlaps_file
], out=filtered_overlaps_file)

run_step([
  reduce_paf_exec,
  overlaps_file,
  filtered_overlaps_file
], out=reduced_overlaps_file)

run_step([
  transform_mcl_input_exec,
  reduced_overlaps_file,
  reads_info_file
], out=mcl_input_file)

if not os.path.exists(os.path.dirname(mcl_out_file)):
  os.makedirs(os.path.dirname(mcl_out_file))

if not os.path.isfile(mcl_out_file):
  run_step([
    mcl_exec,
    mcl_input_file,
    "--force-connected=y",
    "--abc",
    "-te", threads,
    "-I", mcl_granularity,
    "-o", mcl_out_file
  ])

run_step([
  sra_exec,
  sequences_file,
  reduced_overlaps_file,
  mcl_out_file
])

for layout in glob.glob(layout_glob):
  ezra_mappings_all_file = "{}-ezra_mapping_all.paf".format(os.path.splitext(layout)[0])
  run_step([
    minimap2_exec,
    layout,
    sequences_file
  ], out=ezra_mappings_all_file)

  group_id = re.search(r"layout_(\d+)\.fasta", layout).group(1)
  ezra_mappings_reduced_file = "{}-ezra_mapping_reduced.paf".format(os.path.splitext(layout)[0])
  run_step([
    ezra_minimap_reduce_exec,
    mcl_out_file,
    ezra_mappings_all_file,
    group_id
  ], out=ezra_mappings_reduced_file)

  ezra_layout_tmp_file = layout.replace("layout_", "tmp_ezra_layout_")
  run_step([
    ezra_exec,
    sequences_file,
    ezra_mappings_reduced_file,
    layout
  ], out=ezra_layout_tmp_file)

  run_step([
    ezra_adjust_layout_exec,
    layout,
    ezra_layout_tmp_file
  ], out=layout.replace("layout_", "ezra_layout_"))


stat_content_all = []
for layout in glob.glob(ezra_layout_glob):
  if os.path.getsize(layout) == 0:
    continue

  stat_content = ""
  coverages = []
  out, err = run_step([
    rala_stat_exec,
    ",".join(splits),
    ",".join(ref_ids),
    layout,
    sequences_file
  ], out=subprocess.PIPE)
  stat_content += out

  contig_purities_out = "{}-ref_purities.out".format(os.path.splitext(layout)[0])
  out, err = run_step([
    contig_purities_exec,
    ",".join(splits),
    ",".join(ref_ids),
    layout,
    sequences_file
  ], out=contig_purities_out)

  ovlp_stat_content = []
  ovlp_stat_header = []
  for ref, id in zip(ref_files, ref_ids):
    paf_out = "{}-ref_{}.paf".format(os.path.splitext(layout)[0], id)

    run_step([
      minimap2_exec,
      layout,
      ref
    ], out=paf_out)

    out, err = run_step([
      ovlp_stat_exec,
      paf_out,
      contig_purities_out
    ], out=subprocess.PIPE)

    print(out)
    print(out.strip().split("\n"))
    ovlp_stat_content.append([line.split(",")[1] for line in out.strip().split("\n")])
    ovlp_stat_header = [line.split(",")[0] for line in out.strip().split("\n")]

  stat_content_summary = "\n".join([
    ",".join(
      [ovlp_stat_header[i]] +
      [entry[i] for entry in ovlp_stat_content]
    )
    for i in range(len(ovlp_stat_header))
  ]) + "\n,\n,\n"
  stat_content += stat_content_summary

  coverages = [
    [float(entry[i][:-1]) for entry in ovlp_stat_content]
    for i in range(len(ovlp_stat_header)) if ovlp_stat_header[i].startswith('Cover')
  ][0]

  stat_content_all.append((coverages, stat_content, stat_content_summary))

stat_content_all = sorted(stat_content_all, key=lambda x: max(x[0]), reverse=True)

with open(stat_out_file, 'w') as f:
  f.write("".join([s[1] for s in stat_content_all]))

with open(stat_out_summary_file, 'w') as f:
  f.write("".join([s[2] for s in stat_content_all]))

run_step([
  cluster_results_exec,
  reads_info_file,
  mcl_out_file
], out=cluster_results_file)


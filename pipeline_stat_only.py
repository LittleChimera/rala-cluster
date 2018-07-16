#!/usr/bin/python3
from __future__ import print_function
import sys, os, subprocess, multiprocessing, glob

def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

version = "no-cluster-expanded"

threads = str(multiprocessing.cpu_count())

sequences_dir = '/home/lskugor/joined_data'
overlaps_dir = '/home/lskugor/overlaps'
reads_info_dir = '/home/lskugor/reads_info'
overlaps_dir = '/home/lskugor/overlaps'
mcl_input_dir = '/home/lskugor/mcl/input'
mcl_output_dir = '/home/lskugor/mcl/output'
rala_out_dir = '/home/lskugor/ra/rala_no_cluster'
single_sequence_dir = '/home/lskugor/examples/bacteria_data'
splits_dir = '/home/lskugor/splits'
# filtered_overlaps_dir = '/home/lskugor/filtered_overlaps'

reduce_paf_exec = '/home/lskugor/dnba-mcl/scripts/reduce_paf.py'
filter_bad_ovlps_exec = '/home/lskugor/dnba-mcl/scripts/filter_bad_overlaps.py'
splits_exec = '/home/lskugor/dnba-mcl/scripts/splits.py'
reads_info_exec = '/home/lskugor/dnba-mcl/scripts/reads_info.py'
join_reads_exec = '/home/lskugor/dnba-mcl/scripts/join_reads.py'
rala_stat_exec = '/home/lskugor/dnba-mcl/scripts/rala_stat.py'
contig_purities_exec = '/home/lskugor/dnba-mcl/scripts/contig_purities.py'
ovlp_stat_exec = '/home/lskugor/dnba-mcl/scripts/stats_ovlp.py'
transform_mcl_input_exec = '/home/lskugor/dnba-mcl/scripts/transform_info.py'
cluster_results_exec = '/home/lskugor/dnba-mcl/scripts/cluster_results.py'
mcl_exec = '/home/lskugor/local/bin/mcl'
sra_exec = '/home/lskugor/ra/sra.py'
minimap2_exec = '/home/lskugor/minimap2/minimap2'
rclone_exec = '/home/lskugor/local/bin/rclone'

mcl_granularity = "1.10"

ref_ids = sys.argv[1:]
ref_ids_str = "-".join(ref_ids)

# filtered_overlaps_file = os.path.join(overlaps_dir, "fbo_{}.out".format(ref_ids_str))
reduced_overlaps_file = os.path.join(overlaps_dir, "reduced_overlaps_{}_pb.paf".format(ref_ids_str))
ref_files = [os.path.join(single_sequence_dir, "NCTC{}_ref.fasta".format(id)) for id in ref_ids]
ref_sequences_files = [os.path.join(single_sequence_dir, "NCTC{}_formatted_reads.fastq".format(id)) for id in ref_ids]
sequences_file = os.path.join(sequences_dir, "joined_reads_{}.fastq".format(ref_ids_str))
reads_info_file = os.path.join(reads_info_dir, "reads_info_{}.out".format(ref_ids_str))
overlaps_file = os.path.join(overlaps_dir, "overlaps_{}_pb.paf".format(ref_ids_str))
# coverages_file = os.path.join(coverages_dir, "coverages_{}_pb.out".format(ref_ids_str))
mcl_input_file = os.path.join(mcl_input_dir, "graph_{}_pb.in".format(ref_ids_str))
mcl_out_file = os.path.join(mcl_output_dir, "graph_{}_pb_{}.out".format(ref_ids_str, mcl_granularity.replace('.', '_')))
layout_out_dir = os.path.join(rala_out_dir, "layout_{}".format(ref_ids_str))
layout_glob = str(os.path.join(layout_out_dir, "layout".format(ref_ids_str))) + ".fasta"
stat_out_file = os.path.join(layout_out_dir, "stat.csv")
stat_out_summary_file = os.path.join(layout_out_dir, "stat-summary.csv")
cluster_results_file = os.path.join(layout_out_dir, "cluster_results.csv")
splits = []
for id in ref_ids:
  with open(os.path.join(splits_dir, "split-{}.out".format(id)), 'r') as f:
    splits.append(f.read().strip())

def run_step(args, out=None, err=None):
  print(args)
  print(out, err)
  if out != None and os.path.isfile(out):
    eprint('Results already exist for stdout={}'.format(out))
    return

  if type(out) is str:
    out = open(out, 'w')
  if type(err) is str:
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



stat_content_all = []
for layout in glob.glob(layout_glob):
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

# run_step([
#   cluster_results_exec,
#   reads_info_file,
#   mcl_out_file
# ], out=cluster_results_file)

run_step([
  rclone_exec,
  "sync",
  rala_out_dir,
  "gcloudluxihbk:v{}".format(version),
  "--include",
  os.path.join(os.path.basename(layout_out_dir), "*.csv")
])

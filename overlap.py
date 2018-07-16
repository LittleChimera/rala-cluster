class Overlap:
  def __init__(self, target, start, end, target_length):
    self.target = target
    self.start = start
    self.end = end
    self.target_length = target_length

def parse_overlap(line):
  # print(line)
  return Overlap(int(line[0]), int(line[2]), int(line[3]), int(line[1]))

def parse_paf_line(line):
  line = line.split('\t')
  return parse_overlap(line[:4]), parse_overlap(line[5:9])
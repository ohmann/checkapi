"""
<author>
  Savvas Savvides

<created>
  May 2013

<description>
  Uses the parser to get a list of actions and uses these actions to generate
  io statistics.

  This is meant to be a quick plugin to demonstrate the parser's usability. This 
  is not meant to be an optimal implementation
"""

import os
import sys

import parser_truss_calls
import parser_strace_calls

stats = {"reads":0, "read_buf":0, "read_data":0, "read_errs":0, 
         "writes":0, "write_buf":0, "write_data":0, "write_errs":0}

MAX = 10000
read_err_labels = {}
read_sizes = {100:0, 1000:0, MAX:0}
read_over = 0

write_err_labels = {}
write_sizes = {100:0, 1000:0, MAX:0}
write_over = 0


file_paths = []
syscall_count = {"read":0, "write":0}

actions_with_path = ['open', 'creat', 'statfs', 'access', 'stat', 
                     'link', 'unlink', 'chdir', 'rmdir', 'mkdir']

def print_io_stats():
  """
    <Purpose>
      Print all io statistics

    <Arguments>
      None

    <Returns>
      None
  """
  print "I/O System call count:"
  for s in syscall_count:
    print "%10s: %d" %(s, syscall_count[s])
  print

  if syscall_count["read"] > 0:
    print "- average buffer size per read syscall: ", (stats["read_buf"] / syscall_count["read"])
    print "- average data read per read syscall:   ", (stats["read_data"] / syscall_count["read"])
    
    print "Number of reads per size:"
    for size in sorted(read_sizes):
      print "<" + str(size) + "b:" + str(read_sizes[size]) + ",",
    print ">=" + str(MAX) + "b:" + str(read_over)

    print "Number of read errors:"
    if len(read_err_labels) == 0:
      print "    None"
    else:
      for err in read_err_labels:
        print "    ", err, ": ", read_err_labels[err]

  print
  if syscall_count["write"] > 0:
    print "- average buffer size per write syscall:  ", (stats["write_buf"] / syscall_count["write"])
    print "- average data written per write syscall: ", (stats["write_data"] / syscall_count["write"])
    
    print "Number of writes per size:"
    for size in sorted(write_sizes):
      print "<" + str(size) + "b:" + str(write_sizes[size]) + ",",
    print ">=" + str(MAX) + "b:" + str(write_over)

    print "Number of write errors:"
    if len(write_err_labels) == 0:
      print "    None"
    else:
      for err in write_err_labels:
        print "    ", err, ": ", write_err_labels[err]
  
  print
  print "File paths:"
  for f in file_paths:
    print "    ", f
  print



def io_stat(actions):
  """
    <Purpose>
      Given a list of actions, it generates network statistics

    <Arguments>
      actions: A list of actions from a parsed trace

    <Returns>
      None
  """
  for action_index in range(len(actions)):
    action = actions[action_index]

    # get the name of the syscall and remove the "_syscall" part at the end.
    action_name = action[0][:action[0].find("_syscall")]
    

    if action_name == "read":
      # ('read_syscall', (3, 20), (20, ('abcdefghijklmnopqrst',)))
      if action[2][0] != -1:
        syscall_count["read"] += 1
        stats["read_buf"] += action[1][1]
        read_size = action[2][0]
        stats["read_data"] += read_size

        added = False
        for size in sorted(read_sizes):
          if read_size < size:
            read_sizes[size] += 1
            added = True
            break

        if not added:
          read_over += 1

      else:
        stats["read_errs"] += 1
        err_label = action[2][1]
        if err_label in read_err_labels:
          read_err_labels[err_label] += 1
        else:
          read_err_labels[err_label] = 1

    if action_name == "write":
      # ('write_syscall', (3, 'Sample output text\n', 19), (19, None))
      if action[2][0] != -1:
        syscall_count["write"] += 1
        stats["write_buf"] += action[1][2]
        write_size = action[2][0]
        stats["write_data"] += write_size

        added = False
        for size in sorted(write_sizes):
          if write_size < size:
            write_sizes[size] += 1
            added = True
            break

        if not added:
          write_over += 1

      else:
        stats["write_errs"] += 1
        err_label = action[2][1]
        if err_label in write_err_labels:
          write_err_labels[err_label] += 1
        else:
          write_err_labels[err_label] = 1

    # keep track of all the file paths.
    if action_name in actions_with_path:
      if action_name in syscall_count:
        syscall_count[action_name] += 1
      else:
        syscall_count[action_name] = 1

      path = action[1][0]
      if path not in file_paths:
        file_paths.append(path)



if __name__ == "__main__":
  if len(sys.argv) < 2 or len(sys.argv) > 3:
    raise Exception("Please provide: trace file [file_path]")
  
  fh = open(sys.argv[1], "r")
  actions = parser_strace_calls.parse_trace(fh)
  
  io_stat(actions)
  print_io_stats()
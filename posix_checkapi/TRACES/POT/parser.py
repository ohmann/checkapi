"""
<Program>
  parser.py

<Started>
  April 2013

<Author>
  Savvas Savvides <savvas@nyu.edu>

<Purpose>
  This is the posix parser used to parse traces and generate the initial file
  system state. The parser supports traces gathered using strace, truss and 
  dtrace as shown below:
  
      strace -v -f -s1024 -o output_filename command
      
      truss -f -rall -wall -vall -o output_filename command
      
      dtrace_bsd.d -o output_filename -c "command"

      dtrace_osx.d -o output_filename -c "command"

  strace is used to gather traces on Linux systems. truss is used to gather
  traces on Solaris and dtrace is used to gather traces on BSD and OSX systems.
  Additional information on how to gather traces in each of these operating 
  systems is provided in the README file under each OS's directory.

  The initial file system state is represented as a Lind FS. The latter is made 
  up of a lind.metadata file and a set of linddata.# files. Once these files are
  genereated, a trace bundle is constructed which consists of:
    - the original trace file (strace or truss output file)
    - a file containing the parsed trace (a list of all parsed actions pickled)
    - the Lind FS files.
"""

import os
import sys
import shutil
import tarfile
import cPickle

import generate_lind_fs
import parser_truss_calls
import parser_strace_calls

DEBUG = False

"""
Given a path to a trace file, this function performs the following operations:
A. Parses the system calls from the trace file.
B. Generates the Lind File System.
    a. Find all file paths involved in the system calls parsed in the previous 
       step.
    b. Based on the system call outcome decide whether the files referenced by 
       these file paths existed in the POSIX fs at the time the trace file was 
       generated.
    c. If it did, generate that file in the Lind fs, ignore otherwise.
    d. Any previous Lind fs files are removed and overridden.
C. Generates a trace bundle.
    a. Serializes and stores the parsed trace actions.
    b. Generates a tarfile containing the original trace file, the serialized 
       parsed trace file and the Lind fs data and metadata files.
    c. Removes original trace file, serialized file and Lind fs files.
""" 
def generate_trace_bundle(trace_path, parser=None):
  if parser == None:
    # parser was not given. try to infer from the file extension.
    if trace_path.endswith(".strace"):
      parser = "strace"
    elif trace_path.endswith(".truss"):
      parser = "truss"
    elif trace_path.endswith(".dtrace"):
      parser = "dtrace"
    else:
      raise Exception("Could not infer parser from the file extension")
  
  # dtrace traces are parsed the exact same way as strace traces.
  if parser == "dtrace":
    parser = "strace"

  assert(parser in ["strace", "truss"])

  fh = open(trace_path, "r")
  
  # parse actions from file, using the correct parser
  actions = None
  if parser == "strace":
    actions = parser_strace_calls.parse_trace(fh)
  elif parser == "truss":
    actions = parser_truss_calls.parse_trace(fh)
  else:
    raise Exception("Unknown parser when attempting to parse trace.")
  
  fh.close()

  if DEBUG:
    for action in actions:
      print action

  # generate the initial file system needed by the model.
  generate_lind_fs.generate_fs(actions, trace_path)
  
  # pickle the trace
  pickle_name = "actions.pickle"
  pickle_file = open(pickle_name, 'w')
  cPickle.dump(actions, pickle_file)
  pickle_file.close()

  # Now we have everything we need, create the trace bundle which will include 
  # the trace pickle and the lind fs files.
  
  # first find a name for the bundle archive.
  head, bundle_name = os.path.split(trace_path)
  
  # if the bundle_name already exists, append a number.
  temp_count = ''
  bundle_extension = ".trace_bundle"
  while os.path.exists(bundle_name + temp_count + bundle_extension):
    if temp_count == '':
      temp_count = '1'
    else:
      temp_count = str(int(temp_count) + 1)
  bundle_name += temp_count + bundle_extension
  
  # Create the bundle archive.
  tar = tarfile.open(bundle_name, "w")
  
  # add the original trace file.
  original_trace_name = "original_trace." + parser
  # let's copy it locally and rename it first.
  shutil.copyfile(trace_path, original_trace_name)
  tar.add(original_trace_name)

  # add the pickle file
  tar.add(pickle_name)
  
  # add the lind fs metadata file
  if not os.path.exists("lind.metadata"):
    raise Exception("Lind fs metadata file not found.")
  tar.add("lind.metadata")
  
  # add the lind fs data files
  for fname in os.listdir(os.getcwd()):
    if fname.startswith("linddata."):
      tar.add(fname)
  
  tar.close()
  
  # Finally, clean up all intermediate files
  os.remove(original_trace_name)
  os.remove(pickle_name)
  os.remove("lind.metadata")
  for fname in os.listdir(os.getcwd()):
    if fname.startswith("linddata."):
      os.remove(fname)





if __name__ == "__main__":
  if len(sys.argv) < 2 or len(sys.argv) > 3:
    raise Exception("Incorrect number of command line arguments.\n" + 
                    "Usage: python " + sys.argv[0] + 
                    " trace_file [parser (strace/truss/dtrace)]")
  
  trace_path = sys.argv[1]
  
  # if the parser was given explicitly as a third argument, use it
  if len(sys.argv) == 3:
    generate_trace_bundle(trace_path, sys.argv[2])
  else:
    generate_trace_bundle(trace_path)

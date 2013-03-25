"""
<Program>
  posix_strace_parser.py

<Started>
  February 2013

<Author>
  Savvas Savvides

<Purpose>
  This is the parser that translates traces from strace ouput format
  to the intermediate representation, as it is defined in the file
  posix_intermediate_representation.py. It provides a single public
  function which takes as argument an open file and returns a list
  containing all the traces parsed. The file must contain one trace
  per line and each line must follow the strace output format.

  Example of using this module:

    import posix_strace_parser
    fh = open(TRACE_FILE_NAME, "r")
    traces = get_traces(fh)

  The above code will return a list and store it in traces. Each
  entry of this list represents a system call in its intermediate
  representation. The format of the intermediate representation is 
  given below:
  ('syscallName_syscall', (arg1, arg2, ...), (return1, return2))

  The above format, represents a single entry of the list returned.
  It is a tuple that contains three elements. The first elemetns is a
  string made up from the name of the system call (eg open, access),
  followed by the set string '_syscall' (eg open_syscall,
  access_syscall). The second element is a tuple that contains all
  the value arguments passed to that system call. The final element
  is another tuple containing all the return values of the system
  call. Each of the arguments or the return values can be of any type
  including lists. In some cases it is possible that the same
  argument or return value will have different type in different
  calls of the same system call. The order of the combination of
  arguments and return values in the intermediate representation does
  not necessarily match the order in which they appear in the strace
  output format. Although the order of arguments and return values
  separately does follow the order in which they appear in the strace
  output format. In other words, some arguments when parsed could be
  moved to the return value tuple. This happens if the argument
  passed is used as a way to return a value rather than to pass a
  value to the system call. For example passing a pointer of a
  structure to be filled. More information about the intermediate
  representation of each individual system call can be found in the
  posix_intermediate_representation.py file.

  Traces for this module (Strace):
  Before gathering traces for this module consider going through the
  man pages of strace. strace provides many options that can affect
  the output format. The suggested options for gathering traces for
  this module are the following:
  strace -v -f -s1024 -o output_filename command

  -v print structure values unabbreviated.
  -f traces child processes
  -s1024 tells strace to allow string arguments in system calls up to
  1024 characters. If this command is skipped, strace will truncate
  strings exceeding 32 characters.

"""

from posix_intermediate_representation import *
import sys
import posix_generate_fs

# turn message printing on or off.
DEBUG = False


###########
# STRUCTS #
###########
class UnfinishedSyscall(object):
  """
  If a syscall is interapted or blocked, strace will split it in multiple lines.
  Example:
  19176 accept(3, <unfinished ...>
  19175 connect(5, {sa_family=AF_INET, sin_port=htons(25588), sin_addr=inet_addr("127.0.0.1")}, 16) = 0
  19176 <... accept resumed> {sa_family=AF_INET, sin_port=htons(42572), sin_addr=inet_addr("127.0.0.1")}, [16]) = 4

  This object is used to store the information from the first half of
  the system call until the remaining of the system call is found.
  """
  def __init__(self, pid, syscall_name, firstHalf):
    self.pid = pid
    self.syscall_name = syscall_name
    self.firstHalf = firstHalf
  def __str__(self):
    line = str([self.pid, self.syscall_name, self.firstHalf])
    return line

###################################
# Public function of this module. #
###################################
def get_traces(fh):
  # this list will hold all the parsed syscalls
  traces = []
  # this list will hold all pending (i.e unfinished) syscalls
  unfinished_syscalls = []
  
  # process each line
  for line in fh:
    line = line.strip()
    
    if DEBUG:
      print line
        
    # Ignore lines that indicate signals. These lines start with
    # either "+++" or "---". Eg:
    # --- SIGINT (Interrupt) ---
    # +++ killed by SIGINT +++
    if line[:3] in ['+++', '---']:
      continue

    # Is the syscall unfinished?
    if line.find("<unfinished ...>") != -1:
      # Save the unfinished syscall and ignore lines that hold no
      # other information.
      if line != "<unfinished ...>":
        _saveUnfinishedSyscall(line, unfinished_syscalls)
      continue

    # Is the syscall resuming?
    if line.find("<... ") != -1 and line.find(" resumed>") != -1:
      line = _resumeUnfinishedSyscall(line, unfinished_syscalls)
      if line == -1: 
        # unfinished syscall not found in unfinished_syscalls list
        continue

    # Ignore lines starting with Process:
    if line[:line.find(" ")] == "Process":
      continue
    
    # Ignore incomplete syscall lines without '(', ')', and '='
    if line.find('(') == -1 or line.find(')') == -1 or line.find('=') == -1:
      continue
    
    # Parser the syscall name.
    if line[0] == '[':
      # format: [pid 12345] syscall_name(...
      syscall_name = line[line.find(']')+2:line.find('(')]
    elif len(line[:line.find('(')].split(" ")) > 1:
      # format: 12345 syscall_name(...
      syscall_name = line[:line.find('(')].split(" ")[-1]
    else:
      # format: syscall_name(...
      syscall_name = line[:line.find('(')]

    # Get the parameters.
    parameterChunk = line[line.find('(')+1:line.rfind('=')].strip()
    # Remove right bracket and split.
    parameters = parameterChunk[:-1].split(", ")
    # if the syscall is getdents, keep only the first and last 
    # parameters.
    if syscall_name.startswith("getdents"):
      parameters = [parameters[0], parameters[-1]]
    # Fix errors from split on messages
    _mergeQuoteParameters(parameters)

    # Get the return part.
    straceReturn = line[line.rfind('=')+1:].strip()
    if straceReturn.find("(flags ") != -1:
      # handle fcntl return part. I.e use the set of flags instead
      # of their hex representation.
      # example:
      # fcntl64(4, F_GETFL) = 0x402 (flags O_RDWR|O_APPEND)
      # parse the part between '(flags' and ')'
      straceReturn = straceReturn[straceReturn.find("(flags ") +
                     len("(flags "):straceReturn.rfind(")")]
      straceReturn = (straceReturn, None)
    else:
      spaced_results = straceReturn.split(" ")
      if len(spaced_results) > 1:
        # keep only the first part.
        straceReturn = straceReturn[:straceReturn.find(" ")]
      try: 
        straceReturn = int(straceReturn) # result can also be a '?'
      except ValueError:
        pass
      # in case of an error include the error name as well.
      if straceReturn == -1 and len(spaced_results) > 1:
        straceReturn = (straceReturn, spaced_results[1])
      else:
        # if no error, use None as the second return value
        straceReturn = (straceReturn, None)

    trace = parse_trace(syscall_name, parameters, straceReturn)
    
    if trace != UNIMPLEMENTED_ERROR:
      traces.append(trace)
  
  # display all skipped syscall_names.
  if(DEBUG):
    print "\nSkipped System Calls"
    for skipped in SKIPPED_SYSCALLS:
      print skipped + ": " + str(SKIPPED_SYSCALLS[skipped])
  
  # generate the initial file system needed by the model.
  posix_generate_fs.generate_fs(traces, "posix_fs")

  return traces


#####################
# Helper Functions. #
#####################
def _saveUnfinishedSyscall(line, unfinished_syscalls):
  """
  Save unfinished system calls in unfinished_syscalls list until they
  are resumed.
  Each entry is defined by the pid and the system call name.
  """
  try:
    # get pid and syscall name from format: [pid 12345] syscall_name(...
    pid = int(line[line.find(" ")+1:line.find("]")])
    syscall_name = line[line.find("]")+1:line.find("(")].strip()
  except ValueError:
     # get pid and syscall name from format: 12345 syscall_name(...
    pid = int(line[:line.find(" ")])
    syscall_name = line[line.find(" ")+1:line.find("(")].strip()

  if syscall_name in HANDLED_SYSCALLS_INFO:
    unfinished_syscalls.append(UnfinishedSyscall(pid, syscall_name, line[:line.find("<unfinished ...>")].strip()))
    

def _resumeUnfinishedSyscall(line, unfinished_syscalls):
  """
  Resume a previously unfinished system call. Search for the  system
  call in unfinished_syscalls based on the pid and the system call 
  name, and if found merge current line (second half of system call)
  with the first half previously saved.
  """
  try:
    # parses format: [pid 12345] syscall_name(...
    pid = int(line[line.find(" ")+1:line.find("]")])
  except ValueError:
    try:
      # parses format: 12345 syscall_name(...
      pid = int(line[:line.find(" ")])
    except ValueError:
      raise Exception("Failed to parse pid. Unexpected format.")
  
  syscall_name = line[line.find("<... ") + 5:line.find(" resumed>")]

  # find unfinished system call
  unfinished_syscalls_index = None
  for index in range(0, len(unfinished_syscalls), 1):
    if unfinished_syscalls[index].pid == pid and unfinished_syscalls[index].syscall_name == syscall_name:
      unfinished_syscalls_index = index
      break

  if unfinished_syscalls_index == None:
    if DEBUG:
      print "Pending syscall not found.\n"
    return -1
  else:
    second_half = line[line.find("resumed>")+8:].strip()
    if second_half[0] != ')':
      second_half = " " + second_half

    pending = unfinished_syscalls[unfinished_syscalls_index]
    line = pending.firstHalf + second_half
    unfinished_syscalls.pop(unfinished_syscalls_index)

    return line


def _mergeQuoteParameters(parameters):
  if len(parameters) <= 1:
    return
  index = 0
  while index < len(parameters):
    if parameters[index].startswith("\""):
      # The only quote is the first quote which means the 
      # sentence got split and should be put back together.
      while index+1 < len(parameters):
        if _endsInUnescapedQuote(parameters[index].strip(".")):
          break
        parameters[index] += ", " + parameters[index+1]
        parameters.pop(index+1)
    index += 1


def _endsInUnescapedQuote(string):
  if not string or string[-1] != '"':
    return False
  for index in range(-2, -len(string)-1, -1):
    if string[index] != '\\':
      return index % 2 == 0
  return False


#'''
# For testing purposes...
def main():
  if len(sys.argv) < 2:
    raise Exception("Too few command line arguments")

  fh = open(sys.argv[1], "r")
  trace = get_traces(fh)
  for action in trace:
    if len(sys.argv) > 2:
      if sys.argv[2]+"_syscall" == action[0]:
        print "Action: ", action
    else:
      print "Action: ", action
main()
#'''
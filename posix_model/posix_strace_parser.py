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
    traces = getTraces(fh)

  The above code will return a list and store it in traces. Each
  entry of this list represents a system call in its intermediate
  representation. The format of the intermediate representation is 
  given below:
  ('syscallName_syscall', (arg1, arg2, ...), (return1, return2, ...))

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
  the output format. The suggesteed options for gathering traces that
  can be used in this module is as follows:
  strace -f -s1024 -o output_filename command

  -f option tells strace to trace child processes
  -s1024 tells strace to allow string arguments in system calls up to
  1024 characters. If this command is skipped, strace will truncate
  strings that exceed 32 characters.

"""
dy_import_module_symbols("posix_intermediate_representation")

#############
# CONSTANTS #
#############
# this error is used to indicate that a system call found in the
# trace file is not handled by the parser.
UNIMPLEMENTED_ERROR = -1
# turn message printing on or off.
DEBUG = True


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

# This dictionary is used to keep track of which syscalls are skipped
# while parsing and how may times each syscall was skipped.
SKIPPED_SYSCALLS = {}


###################################
# Public function of this module. #
###################################
def gettraces(fh):
  traces = []
  unfinished_syscalls = []
  
  # process each line
  for line in fh:
    line = line.strip()
    
    if DEBUG:
      log(line, "\n")
        
    # Ignore lines that indicate signals. These lines start with
    # either "+++" or "---". Eg:
    # --- SIGINT (Interrupt) ---
    # +++ killed by SIGINT +++
    if line[:3] in ['+++', '---']:
      continue

    # Did the syscall get interrupted?
    if line.find("<unfinished ...>") != -1:
      # Save the unfinished syscall and ignore lines that hold no
      # other information.s
      if line != "<unfinished ...>":
        _saveUnfinishedSyscall(line, unfinished_syscalls)
      continue

    # Is the syscall resuming?
    if line.find("<... ") != -1 and line.find(" resumed>") != -1:
      line = _resumeUnfinishedSyscall(line, unfinished_syscalls)
      if line == -1: # unfinished syscall not found
        continue

    # Ignore lines starting with Process:
    if line[:line.find(" ")] == "Process":
      continue
    
    # Ignore incomplete syscall lines without '(', ')', and '='
    if line.find('(') == -1 or line.find(')') == -1 or line.find('=') == -1:
      continue
    
    # Get the syscall name.
    if line[0] == '[':
      syscall_name = line[line.find(']')+2:line.find('(')]
    elif len(line[:line.find('(')].split(" ")) > 1:
      syscall_name = line[:line.find('(')].split(" ")[-1]
    else:
      syscall_name = line[:line.find('(')]
    
    # Get the function parameters.
    parameterChunk = line[line.find('(')+1:line.rfind('=')].strip()
    # Remove right bracket and split.
    parameters = parameterChunk[:-1].split(", ")
    
    # Get the strace return part.
    straceReturn = line[line.rfind('=')+1:].strip()
    if straceReturn.find("(flags ") != -1:
      # handle fcntl return part. I.e use the set of flags instead
      # of their hex representation.
      straceReturn = straceReturn[straceReturn.find("(flags ") +
                     len("(flags "):straceReturn.rfind(")")]
      straceReturn = (straceReturn, None)
    else:
      spaced_results = straceReturn.split(" ")
      if len(spaced_results) > 1:
        straceReturn = straceReturn[:straceReturn.find(" ")]
      try: 
        straceReturn = int(straceReturn) # result can also be a '?'
      except ValueError:
        pass
      if straceReturn == -1 and len(spaced_results) > 1:
        straceReturn = (straceReturn, spaced_results[1])
      else:
        # if no error, use None as the second return value
        straceReturn = (straceReturn, None)

    trace = _process_trace(syscall_name, parameters, straceReturn)
    
    if trace != UNIMPLEMENTED_ERROR:
      traces.append(trace)
  
  # display all skipped syscall_names.
  log("\n\nSkipped System Calls\n")
  for skipped in SKIPPED_SYSCALLS:
    log(skipped + ": " + str(SKIPPED_SYSCALLS[skipped]) + "\n")
  log("\n")

  return traces


# parses each argument according to what's expected for that syscall
# and translates to the intermediate representation.
def _process_trace(syscall_name, args, result):
  # handle any 'syscall64' the exact same way as 'syscall'
  # eg fstat64 will be treated as if it was fstat
  if syscall_name.endswith('64'):
    syscall_name = syscall_name[:syscall_name.rfind('64')]

  if syscall_name not in HANDLED_SYSCALLS_INFO:
    # Keep track of how many times each syscall was skipped.
    # These information can be printed every time the parser is used
    # to help identify which are the most important and most
    # frequently used syscalls. Subsequently, the parser can be
    # extended to handle these.
    if(syscall_name in SKIPPED_SYSCALLS):
      SKIPPED_SYSCALLS[syscall_name] = SKIPPED_SYSCALLS[syscall_name] + 1;
    else:
      SKIPPED_SYSCALLS[syscall_name] = 1;
    return UNIMPLEMENTED_ERROR

  expected_args = HANDLED_SYSCALLS_INFO[syscall_name]['args']
  args_tuple = ()
  expected_return = HANDLED_SYSCALLS_INFO[syscall_name]['return']
  return_tuple = ()
  
  # Parse the individual arguments of the syscall.
  # Length of args can change. If the syscall contains a string and
  # the string contains ", " the parser will wrongly split the
  # string.
  index = 0
  while index < len(args):
    # Do we have more than the expected arguments?
    if index >= len(expected_args):
      raise Exception("Unexpected argument.")
    
    expected_arg_type = expected_args[index]
    
    # Skip all remaining arguments?
    if isinstance(expected_arg_type, SkipRemaining):
      break
    # Skip this argument?
    if isinstance(expected_arg_type, Skip):
      index += 1
      continue

    # Did the string contain ", "?
    if isinstance(expected_arg_type, Str):
      # if the length of arguments is bigger than the length of the
      # expected arguments then we either intentionally skip some
      # arguments or the string was wrongly split.
      last_arg_type = expected_args[-1]
      if (len(args) > len(expected_args) and not 
             isinstance(last_arg_type, SkipRemaining)):
        end = len(args) - len(expected_args) + index
        for i in range(index, end):
          args[index] += ", " + args[index+1]
          args.pop(index+1)

    argument = expected_arg_type.parse(args[index])
    
    # Did the syscall return an error?
    # in this case the value of structures will not e returned so we
    # stop parsing values.
    if (isinstance(expected_arg_type, StMode) or
        isinstance(expected_arg_type, FType)):
      if argument == MISSING_ARGUMENT:
        break
    
    # Is the argument a return value rather than an argument?
    if expected_arg_type.output:
      return_tuple = return_tuple + (argument,)
    else:
      args_tuple = args_tuple + (argument,)

    index += 1
  
  # parse the return values of the syscall
  for index in range(len(result)):
    expected_return_type = expected_return[index]
    return_argument = expected_return_type.parse(result[index])
    return_tuple = return_tuple + (return_argument,)
  
  # form the intermediate representation.
  trace = (syscall_name+'_syscall', args_tuple, return_tuple)
  return trace


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
    # parses format: [pid 12345] syscall_name(...
    pid = int(line[line.find(" ")+1:line.find("]")])
  except ValueError:
    try:
      # parses format: 12345 syscall_name(...
      pid = int(line[:line.find(" ")])
    except ValueError:
      raise Exception("Failed to parse pid. Unexpected format.")
    else:
      syscall_name = line[line.find(" ")+1:line.find("(")].strip()
  else:
    syscall_name = line[line.find("]")+1:line.find("(")].strip()
  
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
      log("Pending syscall not found.\n\n")
    return -1
  else:
    second_half = line[line.find("resumed>")+8:].strip()
    if second_half[0] != ')':
      second_half = " " + second_half

    pending = unfinished_syscalls[unfinished_syscalls_index]
    line = pending.firstHalf + second_half
    unfinished_syscalls.pop(unfinished_syscalls_index)

    return line


'''
# For testing purposes...
def main():
    fh = open(callargs[0], "r")
    trace = gettraces(fh)
    log("\n")
    for action in trace:
        log("Action: ", action, "\n")

main()
'''
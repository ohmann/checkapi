"""
<Program>
  parser_strace_calls.py

<Started>
  February 2013

<Author>
  Savvas Savvides <savvas@nyu.edu>

<Purpose>
  This is the parser that translates traces from strace ouput format to the 
  intermediate representation, as it is defined in the file 
  parser_intermediate_representation.py. It provides a single public function 
  which takes as argument an open file and returns a list containing all the 
  trace actions parsed. The file must follow the strace output format. 
  Example of using this module:

    import parser_strace_calls
    fh = open(TRACE_FILE_NAME, "r")
    actions = parser_strace_calls.parse_trace(fh)

  The above code will return a list of actions. Each action of this list 
  represents a system call in its intermediate representation. The format of the
  intermediate representation is given below: 
  ('syscallName_syscall', (arg1, arg2, ...), (return1, return2))

  The above format, represents a single entry of the list returned. It is a 
  tuple that contains three elements. The first elemetns is a string made up 
  from the name of the system call (eg open, access), followed by the set string 
  '_syscall' (eg open_syscall, access_syscall). The second element is a tuple 
  that contains all the value arguments passed to that system call. The final 
  element is another tuple containing all the return values of the system call. 
  Each of the arguments or the return values can be of any type including lists. 
  In some cases it is possible that the same argument or return value will have 
  different type in different calls of the same system call. 

  Traces for this module (strace):
  Before gathering traces for this module consider going through the man pages 
  of strace. strace provides many options that can affect the output format. The
  expected options for gathering traces for this module are the following: 

    strace -v -f -s1024 -o output_filename command

    -v print structure values unabbreviated.
    -f trace child processes
    -s1024 allow string arguments in system calls up to 1024 characters.
    If this option is skipped, strace will truncate   strings exceeding
    32 characters.

"""

from parser_helper_calls import *

DEBUG = False

# This dictionary is used to keep track of which syscalls are skipped
# while parsing, and how may times each syscall was skipped.
SKIPPED_SYSCALLS = {}

###########
# STRUCTS #
###########
class UnfinishedSyscall(object):
  """
  If a syscall is interrupted or blocked, strace will split it in multiple lines
  Example:
  19176 accept(3, <unfinished ...>
  19175 connect(5, {sa_family=AF_INET, sin_port=htons(25588), 
                    sin_addr=inet_addr("127.0.0.1")}, 16) = 0
  19176 <... accept resumed> {sa_family=AF_INET, sin_port=htons(42572), 
                              sin_addr=inet_addr("127.0.0.1")}, [16]) = 4

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






def parse_trace(fh):
  # this list will hold all the parsed syscalls
  actions = []

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
    if line.startswith("Process"):
      continue
    
    # Ignore incomplete syscall lines without '(', ')', and '='
    if line.find('(') == -1 or line.find(')') == -1 or line.find('=') == -1:
      continue
    
    # Parse the syscall name.
    if line[0] == '[':
      # format: [pid 12345] syscall_name(...
      syscall_name = line[line.find(']')+2:line.find('(')]
    elif len(line[:line.find('(')].split(" ")) > 1:
      # format: 12345 syscall_name(...
      syscall_name = line[:line.find('(')].split(" ")[-1]
    else:
      # format: syscall_name(...
      syscall_name = line[:line.find('(')]

    # handle any 'syscall64' the exact same way as 'syscall'
    # eg fstat64 will be treated as if it was fstat
    if syscall_name.endswith('64'):
      syscall_name = syscall_name[:syscall_name.rfind('64')]
    
    if syscall_name not in HANDLED_SYSCALLS_INFO:
      # Keep track of how many times each syscall was skipped. These information 
      # can be printed every time the parser is used to help identify which are
      # the most important and most # frequently used syscalls. Subsequently, the
      # parser can be extended to handle these.
      if(syscall_name in SKIPPED_SYSCALLS):
        SKIPPED_SYSCALLS[syscall_name] += 1
      else:
        SKIPPED_SYSCALLS[syscall_name] = 1
      continue

    # Get the parameters.
    parameterChunk = line[line.find('(')+1:line.rfind('= ')].strip()
    # Remove right bracket and split.
    parameters = parameterChunk[:-1].split(", ")
    
    # if the syscall is getdents, keep only the first and last parameters. These
    # are the file descriptor and the buffer size.
    if syscall_name.startswith("getdents"):
      parameters = [parameters[0], parameters[-1]]

    # change number to flag in shutdown according to first letter of second 
    # parameter
    # 7169  shutdown(5, 0 /* receive */)          = 0
    if syscall_name.startswith("shutdown"):
      shutdown_flags = {0:'SHUT_RD', 1:'SHUT_WR', 2:'SHUT_RDWR'}
      parameters[1] = shutdown_flags[int(parameters[1][0])]
    
    # system calls statfs64 or fstatfs64, sometimes include an 
    # unnecessary numeric value as their second parameter. Remove it.
    if syscall_name.startswith("statfs") or syscall_name.startswith("fstatfs"):
      # 22480 statfs64("/selinux", 84, {f_type="EXT2_SUPER_MAGIC", 
      # f_bsize=4096, f_blocks=4553183, f_bfree=741326, f_bavail=510030, 
      # f_files=1158720, f_ffree=509885, f_fsid={-1853641883, 
      # -1823071587}, f_namelen=255, f_frsize=4096}) = 0
      if parameters[1].isdigit():
        parameters.pop(1)

    # TODO: add support for fcntl third parameter according to second parameter.
    if syscall_name.startswith("fcntl"):
      # keep only the first two paramenters
      parameters = [parameters[0], parameters[1]]

    # Fix errors from split on messages
    mergeQuoteParameters(parameters)

    # Get the return part.
    straceReturn = line[line.rfind('=')+1:].strip()
    if syscall_name.startswith("fcntl") and straceReturn.find("(flags ") != -1:
      # handle fcntl return part. I.e use the set of flags instead
      # of their hex representation.
      # example:
      # fcntl64(4, F_GETFL) = 0x402 (flags O_RDWR|O_APPEND)
      # replace the hex part: 0x402 with the flags O_RDWR|O_APPEND
      # get the part between '(flags' and ')'
      straceReturn = straceReturn[straceReturn.find("(flags ")+7:
                                  straceReturn.rfind(")")]
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

    action = parse_syscall(syscall_name, parameters, straceReturn)
    
    if action != UNIMPLEMENTED_ERROR:
      actions.append(action)
  
  # display all skipped syscall names.
  if(DEBUG):
    print "\nSkipped System Calls"
    for skipped in SKIPPED_SYSCALLS:
      print skipped + ": " + str(SKIPPED_SYSCALLS[skipped])
  
  return actions


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




if __name__ == "__main__":
  import sys

  if len(sys.argv) != 2:
    raise Exception("Give trace file")

  actions = parse_trace(open(sys.argv[1], "r"))
  
  """
  for action in actions:
    print action
    print
  """
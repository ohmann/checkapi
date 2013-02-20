# TODO: FCNTL
# TODO: Handle Result


###########
# IMPORTS #
###########
dy_import_module_symbols("intermediate_representation")


#############
# CONSTANTS #
#############
FILE_NAME = "all.strace" # input file
UNIMPLEMENTED_ERROR = -1
SIGS = ["---", "+++"]
DEBUG = False


###########
# STRUCTS #
###########
class UnfinishedSyscall(object):
  def __init__(self, pid, command, firstHalf):
    self.pid = pid
    self.command = command
    self.firstHalf = firstHalf

  def __str__(self):
    line = str([self.pid, self.command, self.firstHalf])
    return line

SKIPPED_SYSCALLS = {}


###################################
# Public function of this module. #
###################################
def getTraces(fh):
  TRACES = []
  unfinished_syscall = []
  
  # process each line
  for line in fh:
    line = line.strip()
    
    if DEBUG:
      log(line, "\n")
        
    # Ignore SIGS
    if line[:3] in SIGS:
      if DEBUG:
        log("Ignoring SIG.")
      continue

    # Did the strace get interrupted?
    if line.find("<unfinished ...>") != -1:
      # Ignore lines with only unfinished
      if line != "<unfinished ...>":
        saveUnfinishedSyscall(line, unfinished_syscall)
      continue

    # Is the strace resuming?
    if line.find("<... ") != -1 and line.find(" resumed>") != -1:
      line = resumeUnfinishedSyscall(line, unfinished_syscall)
      if line == -1: # unfinished syscall not found
        continue
      

    # Ignore lines starting with Process:
    if line[:line.find(" ")] == "Process":
      if DEBUG:
        log("Skipping Process line.")
      continue
    
    # Ignore incomplete strace lines without '(', ')', and '='
    if line.find('(') == -1 or line.find(')') == -1 or line.find('=') == -1:
      if DEBUG:
        log("Skipping Incomplete line.")
      continue
    
    # Get the command name.
    if line[0] == '[':
      command = line[line.find(']')+2:line.find('(')]
    elif len(line[:line.find('(')].split(" ")) > 1:
      command = line[:line.find('(')].split(" ")[-1]
    else:
      command = line[:line.find('(')]
    
    # Get the function parameters.
    parameterChunk = line[line.find('(')+1:line.rfind('=')].strip()
    parameters = parameterChunk[:-1].split(", ")
    
    # Get the result.
    straceResult = line[line.rfind('=')+2:].strip()
    spaced_results = straceResult.split(" ")
    if len(spaced_results) > 1:
      straceResult = straceResult[:straceResult.find(" ")]
    try: 
      straceResult = int(straceResult) # result can also be a '?'
    except:
      pass
    if straceResult == -1 and len(spaced_results) > 1:
      straceResult = (straceResult, spaced_results[1])
    else:
      straceResult = (straceResult, None)

    trace = process_trace(command, parameters, straceResult)
    
    if trace != UNIMPLEMENTED_ERROR:
      TRACES.append(trace)
  
  # display all skipped commands.
  log("\n\nSkipped System Calls\n")
  for skipped in SKIPPED_SYSCALLS:
    log(skipped + ": " + str(SKIPPED_SYSCALLS[skipped]) + "\n")
  log("\n")


  return TRACES



#####################
# Helper Functions. #
#####################
def saveUnfinishedSyscall(line, unfinished_syscall):
  try:
    pid = int(line[line.find(" ")+1:line.find("]")])
    command = line[line.find("]")+1:line.find("(")].strip()
  except:
    pid = int(line[:line.find(" ")])
    command = line[line.find(" ")+1:line.find("(")].strip()
  if command in HANDLED_SYSCALLS_INFO:
    #return [(pid, command)]
    unfinished_syscall.append(UnfinishedSyscall(pid, command, line[:line.find("<unfinished ...>")].strip()))
    if DEBUG:
      log("Unfinished syscall saved.\n\n")
  else:
    if DEBUG:
      log("Skipping unimplimented unfinished syscall.\n\n")
    

def resumeUnfinishedSyscall(line, unfinished_syscall):
  try:
    pid = int(line[line.find(" ")+1:line.find("]")])
  except:
    pid = int(line[:line.find(" ")])
  command = line[line.find("<... ") + 5:line.find(" resumed>")]

  # find unfinished system call
  unfinished_syscall_index = None
  for index in range(0, len(unfinished_syscall), 1):
    if unfinished_syscall[index].pid == pid and unfinished_syscall[index].command == command:
      unfinished_syscall_index = index
      break

  if unfinished_syscall_index == None:
    if DEBUG:
      log("Pending syscall not found.\n\n")
    return -1
  else:
    second_half = line[line.find("resumed>")+8:].strip()
    if second_half[0] != ')':
      second_half = " " + second_half

    pending = unfinished_syscall[unfinished_syscall_index]
    line = pending.firstHalf + second_half
    unfinished_syscall.pop(unfinished_syscall_index)

    return line


# makes use of the intermediate_representation to handle
# each argument according to what's expected.
def process_trace(command, args, result):
  if command.endswith('64'):
    command = command[:command.rfind('64')]

  if command not in HANDLED_SYSCALLS_INFO:
    # keep track of how many times each syscall was skipped.
    if(command in SKIPPED_SYSCALLS):
      SKIPPED_SYSCALLS[command] = SKIPPED_SYSCALLS[command] + 1;
    else:
      SKIPPED_SYSCALLS[command] = 1;

    return UNIMPLEMENTED_ERROR

  expected_args = HANDLED_SYSCALLS_INFO[command]['args']
  expected_return = HANDLED_SYSCALLS_INFO[command]['return']
  args_list = []
  
  # length of args can change hence using a while.
  index = 0
  while index < len(args):
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
      last_arg_type = expected_args[-1]
      if (len(args) > len(expected_args) and not 
             isinstance(last_arg_type, SkipRemaining)):
        end = len(args) - len(expected_args) + index
        for i in range(index, end):
          args[index] += ", " + args[index+1]
          args.pop(index+1)
        

    argument = expected_arg_type.parse(args[index])

    if argument == UNIMPLEMENTED_ERROR:
      return UNIMPLEMENTED_ERROR

    args_list.append(argument)

    index += 1

  # TODO: move result arguments from args_list to result_tuple
  result_tuple = result
  
  trace = (command+'_syscall', tuple(args_list), result_tuple)
  return trace


#'''
# For testing purposes...
def main():
    fh = open(FILE_NAME, "r")
    trace = getTraces(fh)
    log("\n")
    for action in trace:
        log("Action: ", action, "\n")

main()
#'''
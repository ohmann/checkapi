"""
<Program>
  posix_truss_parser.py

<Started>
  February 2013

<Author>
  Savvas Savvides

<Purpose>
  

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

# This dictionary is used to keep track of which syscalls are skipped
# while parsing and how may times each syscall was skipped.
SKIPPED_SYSCALLS = {}


###################################
# Public function of this module. #
###################################
def get_traces(fh):
  traces = []
  # process each line
  for line in fh:
    line = line.strip()
    
    if DEBUG:
      log(line, "\n")
    
    # Ignore incomplete syscall lines without '(', ')', and '='
    if (line.find('(') == -1 or line.find(')') == -1 or 
        (line.find('=') == -1 and line.find('Err') == -1)):
      continue
    
    # Get the syscall name.
    if len(line[:line.find('(')].split()) > 1:
      syscall_name = line[:line.find('(')].split()[-1]
    else:
      syscall_name = line[:line.find('(')]

    # Get the function parameters.
    parameterChunk = line[line.find('(')+1:line.rfind(')')].strip()
    # Remove right bracket and split.
    parameters = parameterChunk.split(", ")
    
    # Get the truss return part.
    trussResult = line[line.rfind(')')+1:]
    if trussResult.find("=") != -1:
      trussResult = line[line.rfind('=')+2:].strip()
    else:
      trussResult = line[line.rfind('Err'):].strip()

    # Is the result a status number or error message?
    spaced_results = trussResult.split()
    if len(spaced_results) > 1:
      trussResult = spaced_results[0]
    try:
      trussResult = int(trussResult)
    except:
      # truss prints Err#INT for errors where INT is the error number.
      if trussResult[:3] == "Err":
        trussResult = -1
      else:
        raise Exception("Unexpected return format " +
                         trussResult)

    if trussResult == -1 and len(spaced_results) > 1:
      trussResult = (trussResult, spaced_results[1])
    else:
      trussResult = (trussResult, None)

    syscall_name = _validate_truss_parameters(fh, syscall_name, 
                       parameters, trussResult)

    trace = _process_trace(syscall_name, parameters, trussResult)
    
    if trace != UNIMPLEMENTED_ERROR:
      traces.append(trace)
  
  # display all skipped syscall_names.
  log("\n\nSkipped System Calls\n")
  for skipped in SKIPPED_SYSCALLS:
    log(skipped + ": " + str(SKIPPED_SYSCALLS[skipped]) + "\n")
  log("\n")

  return traces


def _validate_truss_parameters(fh, syscall_name, args, result):
  # handle any 'syscall64' the exact same way as 'syscall'
  # eg fstat64 will be treated as if it was fstat
  if syscall_name.endswith('64'):
    syscall_name = syscall_name[:syscall_name.rfind('64')]

  if syscall_name == "so_socket":
    # so_socket(PF_INET, SOCK_STREAM, IPPROTO_IP, "", SOV_DEFAULT) = 3
    
    # keep only the first three arguments.
    if len(args) > 3:
      for arg_index in range(len(args)-1, 2, -1):
        args.pop(arg_index)
      return "socket"
  
  elif (syscall_name == "bind" or syscall_name == "connect" or 
        syscall_name == "accept"):
    # 1648: bind(3, 0x080474F0, 16, SOV_SOCKBSD)    = 0
    # 1648:   AF_INET  name = 0.0.0.0  port = 25588
    # 1815/1:   connect(5, 0x080474F0, 16, SOV_DEFAULT)   = 0
    # 1815/1:     AF_INET  name = 0.0.0.0  port = 25588
    # 1698/1:   connect(5, 0x080474F0, 16, SOV_DEFAULT)   Err#146 ECONNREFUSED
    # 1698/1:     AF_INET  name = 0.0.0.0  port = 25588
    
    # keep only the first three arguments.
    if len(args) > 3:
      for arg_index in range(len(args)-1, 2, -1):
        args.pop(arg_index)
    
    (afamily, ip, port) = get_sockaddr(fh)
    args[1] = afamily # replace structure address
    args.insert(2, port)
    args.insert(3, ip)

    try:
      int(args[4])
    except ValueError:
      args[4] = 16

  elif syscall_name == "sendto" or syscall_name == "recvfrom":
    # 3323: sendto(3, 0x08059C1D, 20, 0, 0x080474F0, 16)  = 20
    # 3323:    M e s s a g e   f o r   s e n d t o .\0
    # 3323:   AF_INET  to = 0.0.0.0  port = 25588
    # 3012: sendto(4, 0x0808B9E0, 64, 32768, 0x0806AA90, 16) = 64
    # 3012: \b\019 -\f j\0\0909D14 Q 7 w\v\0\b\t\n\v\f\r0E0F1011121314151617
    # 3012: 18191A1B1C1D1E1F   ! " # $ % & ' ( ) * + , - . / 0 1 2 3 4 5 6 7
    # 3012: AF_INET  to = 173.194.73.105  port = 0
    
    if args[1].startswith("0x"):
      args[1] = get_message(fh, result[0]) # replace string address
    
    (afamily, ip, port) = get_sockaddr(fh)
    args[4] = afamily # replace structure address
    args.insert(5, port)
    args.insert(6, ip)

  elif syscall_name == "send" or syscall_name == "recv":
    # 3340/1:   send(5, "\0\0 cF4", 4, 0)     = 4
    # 3340/1:   send(5, 0x08059BF1, 23, 1)      = 23
    # 3340/1:      N o n e   s h a l l   b e   r e v e a l e d\0
    
    if args[1].startswith("0x"):
      args[1] = get_message(fh, result[0]) # replace string address

  elif (syscall_name == "getsockname" or syscall_name == "getpeername" or
        syscall_name == "setpeername"):
    # 3222/1:   getpeername(5, 0x080474C0, 0x080474D8, SOV_DEFAULT) = 0
    # 3222/1:     AF_INET  name = 127.0.0.1  port = 25588
    # 3217: getsockname(3, 0x080474C0, 0x080474DC, SOV_DEFAULT) = 0
    # 3217:     AF_INET  name = 127.0.0.1  port = 25588
    
    # keep only the first three arguments.
    if len(args) > 3:
      for arg_index in range(len(args)-1, 2, -1):
        args.pop(arg_index)

    (afamily, ip, port) = get_sockaddr(fh)
    args[1] = afamily # replace structure address
    args.insert(2, port)
    args.insert(3, ip)

    # truss does not dereference int*
    args[4] = '16'

  elif syscall_name == "listen" or syscall_name == "shutdown":
    # 1698/2:   listen(3, 5, SOV_DEFAULT)     = 0
    # 1698/2:   shutdown(5, SHUT_RD, SOV_DEFAULT)     = 0
    
    # keep only the first three arguments.
    if len(args) > 2:
      for arg_index in range(len(args)-1, 1, -1):
        args.pop(arg_index)

  elif syscall_name == "read" or syscall_name == "write":
    # 19477: read(3, "Sample output text\n", 20) = 19
    # 19477: write(1, 0xD1E46BA4, 24)     = 24
    # 19477:    w w w . g o o g l e . c o m   i s   a l i v e\n
    
    if args[1].startswith("0x"):
      args[1] = get_message(fh, result[0]) # replace string address
  
  elif syscall_name == "getsockopt" or syscall_name == "setsockopt":
    # 3201/2:   getsockopt(20, SOL_SOCKET, SO_RCVBUF, 0xD169FF10, 0xD169FF0C, SOV_XPG4_2) = 0
    # setsockopt(4, SOL_SOCKET, SO_RCVBUF, 0x080474C4, 4, SOV_DEFAULT) = 0
    
    # keep only the first three arguments.
    if len(args) > 3:
      for arg_index in range(len(args)-1, 2, -1):
        args.pop(arg_index)

  elif (syscall_name == "fstat" or syscall_name == "stat"):
    # 3201/1:   fstat64(6, 0x08047220)        = 0
    # 3201/1:       d=0x00780000 i=185862 m=0100644 l=1  u=0     g=0   
    # 3201/1:   fstat64(6, 0x080472E0)        = 0
    # 3201/1:       d=0x00780000 i=185862 m=0100644 l=1  u=0     g=0     sz=56
    # 3212: stat64("/savvas/syscalls", 0x08047160)    = 0
    # 3212:     d=0x00780000 i=299671 m=0100755 l=1  u=0     g=0     sz=58140

    (st_mode, st_size) = get_stat(fh)
    args[1] = st_mode # replace structure address
    args.insert(2, st_size)
    
  elif (syscall_name == "close" or syscall_name == "access" or
        syscall_name == "chdir" or syscall_name == "rmdir" or 
        syscall_name == "mkdir" or syscall_name == "link" or
        syscall_name == "symlink" or syscall_name == "unlink" or
        syscall_name == "open" or syscall_name == "lseek" or
        syscall_name == "dup" or syscall_name == "dup2" or 
        syscall_name == "fcntl"):
    # 1698: close(3)          = 0
    # 1600: access("syscalls.txt", F_OK)          = 0
    # 1621: chdr(".")          = 0
    # 1621: rmdir("sycalls_dir")          = 0
    # 1621: mkdir("sycalls_dir", 0775)          = 0
    pass

  return syscall_name


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
def get_sockaddr(fh):
  """
  Returns a tuple (family, ip, port)

  The sockaddr structure is given in the line following the current
  line.
  If the line contains the information needed, that line is read
  and the information returned in a tuple.
  If the line is not of the expected format then the file position
  is returned to its original position.
  """
  
  family = UNIMPLEMENTED_ERROR
  ip = UNIMPLEMENTED_ERROR
  port = UNIMPLEMENTED_ERROR

  fpos = fh.tell()
  line = fh.readline()

  # ip can be labeled as "name =" or "to ="
  if (line.find("name =") != -1 or line.find("to =") != -1) and line.find("port =") != -1:
    if line.find("name =") != -1:
      family = line[line.find(":")+1:line.find("name =")].strip()
      ip = line[line.find("name =")+6:line.find("port =")].strip()
    else:
      family = line[line.find(":")+1:line.find("to =")].strip()
      ip  = line[line.find("to =")+4:line.find("port =")].strip()
    port = line[line.find("port =")+6:].strip()
  else:
    fh.seek(fpos)
  
  family = "sa_family=" + family
  ip = 'sin_addr=inet_addr("' + ip + '")'
  port = "sin_port=htons(" + port + ")"

  return (family, ip, port)


def get_message(fh, msglen):
  """Returns the message

  The message is given in the line (or maybe multiple lines) following
  the current line.
  If the line contains the message, that line is read and returned.
  If the line is not of the expected format then the file position
  is returned to its original position.
  """
  
  fpos = fh.tell()
  message = ""
  while len(message) < msglen:
    line = fh.readline()
    # remove pid from message
    line = line[line.find(":")+1:]
    #BUG: what if the message starts with space?
    line = line.strip()
    
    # each character in the message is stupidly space padded.
    random_string = "#*"
    while line.find(random_string) != -1:
      random_string += "*"
    line = line.replace("   ", random_string)
    line = line.replace(" ", "")
    line = line.replace(random_string, " ")

    # translate special characters
    line = line.replace("\\n", "\n")
    line = line.replace("\\r", "\r")
    line = line.replace("\\t", "\t")
    line = line.replace("\\0", "\0")

    message = line

  if len(message) != msglen:
    message = UNIMPLEMENTED_ERROR
    fh.seek(fpos)

  return '"' + message + '"'


def get_stat(fh):
  """
  Returns a tuple (st_mode, st_size)

  The stat structure is given in the line following the current
  line.
  If the line contains the information needed, that line is read
  and the information returned in a tuple.
  If the line is not of the expected format then the file position
  is returned to its original position.
  """
  
  st_mode = UNIMPLEMENTED_ERROR
  st_size = UNIMPLEMENTED_ERROR

  fpos = fh.tell()
  line = fh.readline()

  if line.find("m=") != -1 or line.find("sz=") != -1:
    if line.find("m=") != -1:
     st_mode = line[line.find("m=")+2:line.find("l=")].strip()
    if line.find("sz=") != -1:
      st_size = line[line.find("sz=")+3:].strip()
  else:
    fh.seek(fpos)
  
  st_mode = "st_mode=" + str(st_mode)
  st_size = "st_size=" + str(st_size)

  return (st_mode, st_size)


#'''
# For testing purposes...
def main():
    fh = open(callargs[0], "r")
    trace = get_traces(fh)
    log("\n")
    for action in trace:
        log("Action: ", action, "\n")

main()
#'''
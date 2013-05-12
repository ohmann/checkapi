from parser_intermediate_representation import *

# this error is used to indicate that a system call found in the
# trace file is not handled by the parser.
UNIMPLEMENTED_ERROR = -1

"""
Parses a single trace given the syscall name, the arguments and the
return value of that trace.

Parsing proceeds in 4 steps.
  1. Initialization: Get the expected type of arguments and return values, 
     according to the name of the syscall. Initialize a list for the arguments 
     and a list for the return values and set all values to the Unknown object.
  2. Parsing: For each expected argument and each expected return value, check 
     if the given value is of the expected format and parse it. In case of an 
     unexpected format, raise an exception.
  3. Rearranging: Move some items from the arguments list to the return value 
     list. This happens because some arguments are used to return values rather 
     than to pass values to the system call.
  4. Form IR: Combines the system call name, the argument list and the return 
     value list to construct the Intermediate Representation.
"""
def parse_syscall(syscall_name, args, result):
  if syscall_name not in HANDLED_SYSCALLS_INFO:
    return UNIMPLEMENTED_ERROR

  ##########################
  # 1. Initialization step #
  ##########################
  # get the expected arguments from the intermediate representation.
  expected_args = list(HANDLED_SYSCALLS_INFO[syscall_name]['args'])
  # get the expected return values from the intermediate representation.
  expected_return = list(HANDLED_SYSCALLS_INFO[syscall_name]['return'])
  # Initialize all arguments to Unknown()
  args_list = []
  for arg_index in range(len(expected_args)):
    # call parse with no arguments which will return Unknown 
    args_list.append(expected_args[arg_index].parse())
  # Initialize all return values to Unknown()
  return_list = []
  for return_index in range(len(expected_return)):
    return_list.append(expected_return[return_index].parse())
  
  ###################
  # 2. Parsing step #
  ###################
  # Parse the individual arguments of the syscall.
  # Length of args can change. If the syscall contains a string argument and 
  # the string contained ", " the parser would have wrongly split the string.
  index = 0
  offset = 0
  while index < len(args):
    # Do we have more than the expected arguments?
    if index >= len(expected_args):
      raise Exception("Too many arguments found while parsing.")
    
    # get the expected type for the current argument.
    # What is offset?
    # If the syscall returned an error the value of structure variables will not
    # be returned. Instead, where we expect the first value of the structure 
    # we get the address of the structure and the remaining values are simply 
    # not listed. Using offset we can skip these expected arguments since they
    # are not provided.
    expected_arg_type = expected_args[index + offset]
    
    # Skip all remaining arguments?
    # this type is used to indicate that the remaining arguments
    # should be skipped. This is useful in cases where a system call
    # is partly supported.
    # Consequently, the value of the remaining arguments will be the
    # one given to them in the initialization step.
    if isinstance(expected_arg_type, SkipRemaining):
      break

    # Did the argument contain ", "? A few types can contain a ", " string, in 
    # which case the parser would have wrongly split these in two arguments.
    if(isinstance(expected_arg_type, FFsid) or 
       isinstance(expected_arg_type, StDev) or
       isinstance(expected_arg_type, StSizeOrRdev) or
       isinstance(expected_arg_type, TimeVal)):
      if len(args) > len(expected_args):
        args[index] += ", " + args[index+1]
        args.pop(index+1)
    
    args_list[index+offset] = expected_arg_type.parse(args[index])
    
    # Did the syscall return an error?
    # Deal with the fact that some structure values may not be provided. We can 
    # detect when this happens by checking if the returned "parsed" value of 
    # some expected types is Unknown. How do we deal with this? The values of
    # the expected arguments are set to Unknown and the offset variable is set
    # appropriately so that in the next iteration we parse the correct argument
    # type.
    # Firstly set the offset which indicates how many values after the current 
    # value are missing.
    # Then for each missing value, get its expected type. The final value will
    # in any case be an Unknown object but getting the expected type helps in
    # constructing a more informative Unknown object. Specifically we can run
    # the parse function of this type with no arguments which will return an
    # Unknown object with its expected_type and its given_value variables set
    # appropriately.
    if args_list[index+offset] == Unknown():
      # set the offset value according to what the current type is.
      if(isinstance(expected_arg_type, ZeroOrListOfFlags) and 
         expected_arg_type.label_left == "sa_family="):
        if syscall_name == "recvmsg" or syscall_name == "sendmsg":
          # six additional structure values follow SockFamily in
          # recvmsg and in sendmsg. Hence six values are missing and
          # the offset should be set to six.
          offset = 6
        else:
          # two additional structure values follow SockFamily. Hence
          # two values are missing and the offset should be set to two.
          offset = 2
      elif(isinstance(expected_arg_type, Str) and 
         expected_arg_type.label_left == "f_type="):
        offset = 9
      elif isinstance(expected_arg_type, StDev):
        offset = 11
      # For each missing argument, set its value to Unknown.
      for missing_index in range(1, offset+1):
        missing_arg_type = expected_args[index + missing_index]
        args_list[index + missing_index] = missing_arg_type.parse()
    
    # adjust the expected arguments for sockaddr according to the sock_family
    # The default expected values after a SockFamily are port and ip
    if(isinstance(expected_arg_type, ZeroOrListOfFlags) and 
       expected_arg_type.label_left == "sa_family=" and not
       isinstance(args_list[index], Unknown)):

      # if the family is AF_NETLINK, we need pid and groups.
      if "AF_NETLINK" in args_list[index]:
        expected_args[index+1] = Int(label_left="pid=", output=True)
        expected_args[index+2] = Int(label_left="groups=", 
                                     label_right="}", output=True)

      # if the family is AF_FILE, we need path.
      # 14037 connect(4, {sa_family=AF_FILE, path="/var/run/nscd/socket"}, 110) 
      #                               = -1 ENOENT (No such file or directory)
      if "AF_FILE" in args_list[index]:
        # set port to path instead and remove second expected arg
        expected_args[index+1] = SockPath(label_right="}", output=True)
        del(expected_args[index+2])

    
    index += 1

  # parse the return values of the syscall
  for index in range(len(result)):
    # Do we have more than the expected return values?
    if index >= len(expected_return):
      raise Exception("Too many return values found while parsing.")
    expected_return_type = expected_return[index]
    return_list[index] = expected_return_type.parse(result[index])
  
  #######################
  # 3. Rearranging step #
  #######################
  # Some arguments are used to return a value rather than to pass
  # a value to the syscall. These arguments are moved to the return
  # part of the syscall. How do we know if a given argument should be
  # moved to the return part? Each expected argument type has a
  # variable called output, which if true, indicates just that.
  return_tuple = ()
  # add the expected return values to the return tuple.
  for return_index in range(len(expected_return)):
    return_tuple = return_tuple + (return_list[return_index],)
  
  args_tuple = ()
  args_return_tuple = () # arguments to move in return tuple.
  # if the expected argument is an "output" argument, append it to
  # the return tuple, else append it in the arguments tuple.
  for arg_index in range(len(expected_args)):
    if expected_args[arg_index].output:
      args_return_tuple = args_return_tuple + (args_list[arg_index],)
    else:
      args_tuple = args_tuple + (args_list[arg_index],)
  
  # if the system call returned an error, indicated by a -1, then
  # skip the args_return_tuple
  if return_tuple[0] != -1 and len(args_return_tuple) != 0:
    # if the return_tuple is of format (value1, None) then replace
    # None with the args_return_tuple. Otherwise if the second
    # argument of the return value is not None, raise an Exception.
    if len(return_tuple) == 2 and return_tuple[1] == None:
      return_tuple = (return_tuple[0], args_return_tuple)
    else:
      raise Exception("Trying to add more return values in a " + 
                      "system call which already has two return " + 
                      "values. " + return_tuple)
  
  ###################
  # 4. Form IR step #
  ###################
  # form the intermediate representation.
  return (syscall_name+'_syscall', args_tuple, return_tuple)


"""
Used to fix errors on parsing parameters. Specifically, if a string value in the
trace contains a ", " (without the quotes) the string will be wrongly split in
two parameters. This method searches for parameters that start with a double
quote (indicating that the parameter is a string) and if that parameter does not
end with a double quote (an unescaped double quote, of course) then the string
must have been split. Join this parameter with the next one and repeat the same
procedure to fix.
"""
def mergeQuoteParameters(parameters):
  if len(parameters) <= 1:
    return
  index = 0
  while index < len(parameters):
    # if the parameter starts with a quote but does not end with a quote, the
    # parameter must have been split wrong.
    if parameters[index].startswith("\""):
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
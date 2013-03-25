"""
<Program Name>
  verify-posix.repy

<Started>
  February 12, 2013

<Author>
  Eleni Gessiou <egkesi01@students.poly.edu>
  Savvas Savvides <savvas@nyu.edu>

<Purpose>
  Verifies system call traces against the posix filesystem API.

<Usage>
  NOTE: Must be executed with librepy.repy:
  python verify-posix.py

<Note>
  For posix verification, setting the initial repy model's filesystem in this file:
  check_api_initial_filestate.input
  is not necessary.

"""

import repyhelper
repyhelper.translate_and_import("check_api.repy")
repyhelper.translate_and_import("wrapped_lind_net_calls.py")
repyhelper.translate_and_import("wrapped_lind_fs_calls.py")

import posix_strace_parser.py 


net_syscall_map = {'getsockname_syscall':getsockname_syscall,
               'getpeername_syscall':getpeername_syscall,
               'listen_syscall':listen_syscall,          
               'accept_syscall':accept_syscall,          
               'getsockopt_syscall':getsockopt_syscall,  
               'setsockopt_syscall':setsockopt_syscall,  
               'setshutdown_syscall':setshutdown_syscall,
               'socket_syscall':socket_syscall,          
               'bind_syscall':bind_syscall,              
               'connect_syscall':connect_syscall,        
               'sendto_syscall':sendto_syscall,          
               'send_syscall':send_syscall,              
               'recvfrom_syscall':recvfrom_syscall,      
               'recv_syscall':recv_syscall}

fs_syscall_map = {'access_syscall':access_syscall,
               'chdir_syscall':chdir_syscall,
               'close_syscall':close_syscall,
               'creat_syscall':creat_syscall,
               'dup2_syscall':dup2_syscall,
               'dup_syscall':dup_syscall,
               'fcntl_syscall':fcntl_syscall,
               'fstat_syscall':fstat_syscall,
               'fstatfs_syscall':fstatfs_syscall,
               'getdents_syscall':getdents_syscall,
               'link_syscall':link_syscall,
               'lseek_syscall':lseek_syscall,
               'mkdir_syscall':mkdir_syscall,
               'open_syscall':open_syscall,
               'read_syscall':read_syscall,
               'rmdir_syscall':rmdir_syscall,
               'stat_syscall':stat_syscall,
               'statfs_syscall':statfs_syscall,
               'unlink_syscall':unlink_syscall,
               'write_syscall':write_syscall}

oracle_required_funcs = ['connect_syscall', 'sendto_syscall', 
                         'getsockname_syscall', 'accept_syscall']

# system calls that have a file descriptor as their first argument.
fd_calls = ["fstatfs_syscall", "fstat_syscall", "lseek_syscall", 
            "read_syscall", "write_syscall", "close_syscall", 
            "dup2_syscall", "dup_syscall", "fcntl_syscall", 
            "getdents_syscall", "bind_syscall", "connect_syscall", 
            "sendto_syscall", "send_syscall", "recvfrom_syscall", 
            "recv_syscall", "getsockname_syscall", 
            "getpeername_syscall", "listen_syscall", "accept_syscall", 
            "getsockopt_syscall", "setsockopt_syscall", 
            "setshutdown_syscall"]

filepath_calls = ['statfs_syscall', 'access_syscall', 'link_syscall', 
                  'unlink_syscall', 'stat_syscall', 'chdir_syscall', 
                  'mkdir_syscall', 'rmdir_syscall']


# Jeff-TODO: Probably need to deal with reads on files that we haven't written to? It seems 
#       like we can't verify anything in terms of reads...

posix_fd_map = {}
posix_oracle = []

DEBUG_VERIF = True


# Create string that has a max length, this helps when printing large strings.
def short_string(data, length=800):
  if not isinstance(data, str):
    raise Exception("Unexpected data in short_string.")

  data_short = str(data)[:length]

  if len(str(data)) > len(str(data_short)):
    data_short += "!!SHORTENED STRING!!"
  
  return data_short


# Returns the corresponding fd that the model uses, if it's different
# from what the implementations uses.
def _translate_fd(impl_fd):
  try:
    return posix_fd_map[impl_fd]
  except KeyError:
    #return None
    return impl_fd


# Takes a list of actions in a trace and attempts to execute them in 
# the posix model. We are also responsible for keeping track of
# file-descriptor mappings since the implementation may use different
# ones from us.
def verify_trace(trace):
  
  # a list to hold all the errors occured during the verification step
  ERRORS = []

  # keep track of the number of actions read.
  action_number = 0

  for action in trace:
    action_number += 1

    # for debugging purposes, all the actions that are being attempted
    # can be printed
    if DEBUG_VERIF == True:
      print action_number, ":", action
 
    # unpack the action and the return value
    # the general format of an action is this:
    # (syscall_name, (arguments tuple), (return tuple))
    action_name, action_args, action_return = action
    impl_ret, impl_errno = action_return

    # if impl_ret has an unexpected value print a warning and set it
    # to -1, indicating the action returned an error.
    if impl_ret < -1:
      print "[WARNING] Strange value of return value in the " + \
            "implementation: ", impl_ret
      impl_ret = -1

    # Get the syscall function based on the action_name of the syscall in
    # the action.
    if action_name in net_syscall_map:
      syscall_function = net_syscall_map[action_name]
    elif action_name in fs_syscall_map:
      syscall_function = fs_syscall_map[action_name]
    else:
      print "[WARNING] I don't know this system call: ", action_name
      continue

    # Deal with various fd impl->model replacements.
    if action_name in fd_calls:
      if action_name != "dup2_syscall":
        impl_fd = action_args[0]
        model_fd = _translate_fd(impl_fd)
        # replace fd in args with the new one.
        action_args = (model_fd,) + action_args[1:]
      else:
        model_fd1 = _translate_fd(action_args[0])
        model_fd2 = _translate_fd(action_args[1])
        # replace both fd with the new ones.
        action_args = (model_fd1, model_fd2)
      
      # arguments of the action were changed so update the action.
      action = (action_name, action_args, action_return)
    
    model_errno = None
    try:
      posix_oracle.append((impl_ret, impl_errno))

      # Execute with the model!!
      model_ret = syscall_function(*action_args)

    # If implementation does not implement something so far, make a note of it
    except UnimplementedError, err:
      print 'UnimplmentedError Not Supported!', err, ' : ', action
      continue

    except SyscallError, err:
      model_ret = -1
      model_errno = err[1]
      pass

    # JR: This is a conformance failure, since a POSIX call should 
    # never raise a Repy exception. The Repy model should be
    # transparent to the POSIX model caller.
    except RepyException, err:
      log('ConformanceFaulure! RepyException with action: ', action, '\n')
      raise err

    # if model returns that a fd has been ignored, just print relevant information
    except IgnoredFileDescriptorWarning, err:
      print "IGNORING: ", err[1]
      continue


    # EG: there is no way to verify the results, only its success/failure,
    # because model assigns semi-'random' values. So, just return 'OK'
    if action_name in ['fstat_syscall', 'fstatfs_syscall'] and model_ret != -1 and impl_ret == 0:
      print "OK"

    # Skip file syscalls on files that don't already exist in posix model
    if action_name in filepath_calls:
      if model_errno != impl_errno or model_ret != impl_ret:
        print "IGNORING: " + str(action) + ". Model returned ", model_errno, model_ret, " which do not match with the implementation."
        continue
    
    # If file doesn't exist in POSIX but exists on system (like .so library files), 
    # then add open fd to ignore_fd to ignore future calls to that fd
    if action_name in ['open_syscall', 'creat_syscall']:

      if impl_errno == None and model_errno != impl_errno:
        print "IGNORING: " + str(action) + ", because model returned an error: ", model_errno

        # EG: I have no other option but to use the ignore_fd here, 
        # because the verifier only should check the return value
        ignore_fd.append(impl_ret)

        #EG: remove any mapping between model and impl fd, even if the syscalls fail
        try:
          del posix_fd_map[impl_ret]
        except:
          pass

        continue
    

    # if model returns different fd than the implementation, keep the correspodance
    # EG: I added dup_syscall
    if action_name in ['socket_syscall', 'open_syscall', 'creat_syscall', 'dup_syscall', 'dup2_syscall'] and impl_ret != -1:
      posix_fd_map[impl_ret] = model_ret
      model_ret = impl_ret


    # accept returns a tuple of (ip, port, fd), but we need only the fd
    if action_name  == 'accept_syscall' and impl_ret != -1:
      # check if ip addrs and ports match
      if model_ret[0] == impl_errno[2] and model_ret[1] == impl_errno[1]:
        posix_fd_map[impl_ret] = model_ret[2]
        model_ret = impl_ret
        

    # FS model doesn't need the oracle and a handful of network calls also 
    # don't need it.
    if action_name in fs_syscall_map or action_name not in oracle_required_funcs:
      posix_oracle.pop()



    # VERIFY RESULTS! 
    # Currently we are just printing them out to visually 
    # verify we are getting something sane.
   
    # many syscalls need special care in order to check if the results from
    # the parser match the results from the model. That is because parser's
    # results are general-purpose and more verbose than we need in this project.


    if action_name == "accept_syscall" and impl_ret == model_ret and impl_ret != -1:
      print short_string(action_number) + " OK: " + action_name + short_string(args) + ' -> ' + short_string((impl_ret, impl_errno)) + "  " + short_string((model_ret, model_errno))
    # check if port, ip addr match
    elif (name == 'getpeername_syscall' or action_name == 'getsockname_syscall') and impl_errno[1:3] == model_ret:
      print short_string(action_number) + " OK: " + action_name + short_string(args) + ' -> ' + short_string((impl_ret, impl_errno)) + "  " + short_string((model_ret, model_errno))

    # check the value for the option
    elif action_name == 'getsockopt_syscall' and impl_errno[0] == model_ret:
      print short_string(action_number) + " OK: " + action_name + short_string(args) + ' -> ' + short_string((impl_ret, impl_errno)) + "  " + short_string((model_ret, model_errno))

    elif action_name == 'read_syscall' and impl_ret == model_ret:
      print short_string(action_number) + " OK: " + action_name + short_string(args) + ' -> ' + short_string((impl_ret, impl_errno)) + "  " + short_string((model_ret, model_errno))

    elif impl_ret != model_ret or impl_errno != model_errno:
      print short_string(action_number * num) + " ERROR: " + action_name + short_string(args) + ' -> ' + short_string((impl_ret, impl_errno)) + "  " + short_string((model_ret, model_errno))
      ERRORS.append(short_string(action_number * num) + " ERROR: " + action_name + short_string(args) + ' -> ' + short_string((impl_ret, impl_errno)) + "  " + short_string((model_ret, model_errno)))

    else:
      print short_string(action_number) + " OK: " + action_name + short_string(args) + ' -> ' + short_string((impl_ret, impl_errno)) + "  " + short_string((model_ret, model_errno))

  return ERRORS


def main():
  if len(sys.argv) < 3:
    raise Exception("Too few command line arguments. Usage: " +
                    sys.argv[0] + " <trace file> <error file>")
  
  trace_file = sys.argv[1]
  error_file = sys.argv[2]
  
  # read the trace
  fh = open(trace_file, "r")
  trace = get_traces(fh)
  fh.close()
  
  # run checkAPI
  ERRORS = verify_trace(trace)
  
  print "\n\n\n\n\n"
  
  # write all errors to the error file.
  fh = open(error_file, "w")
  numLines = 0
  for line in ERRORS:
    print short_string(line)
    fh.write(line + "\n")
    numLines += 1
  fh.write(str(numLines) + " error(s)...\n")
  fh.close()

  print short_string(numLines) + " error(s)..."

main()
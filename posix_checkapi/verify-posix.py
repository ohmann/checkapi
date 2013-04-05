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

from repyportability import *
_context = locals()
add_dy_support(_context)

dy_import_module_symbols("check_api.repy")
#dy_import_module_symbols("wrapped_lind_net_calls.py")
#dy_import_module_symbols("wrapped_lind_fs_calls.py")

from posix_strace_parser import *


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
mycontext['posix_oracle'] = []

DEBUG_VERIF = False



# Takes a list of actions in a trace and attempts to execute them in 
# the posix model. We are also responsible for keeping track of
# file-descriptor mappings since the implementation may use different
# ones from us.
def verify_trace(trace):
  
  # a list to hold all the errors occured during the verification step
  ERRORS = []

  # keep track of the number of actions read.
  line_num = 0

  for action in trace:
    line_num += 1

    # for debugging purposes, all the actions that are being attempted
    # can be printed
    if DEBUG_VERIF == True:
      print str(line_num) + ": " + _short_string(action)
 
    # unpack the action and the return value
    # the general format of an action is this:
    # (syscall_name, (arguments tuple), (return tuple))
    syscall_name, syscall_args, syscall_return = action
    syscall_retno, syscall_errno = syscall_return

    # if syscall_retno has an unexpected value print a warning and set it
    # to -1, indicating the action returned an error.
    if syscall_retno < -1:
      print "[WARNING] Strange value of return value in the " + \
            "implementation: ", syscall_retno
      syscall_retno = -1

    # Get the syscall function based on the syscall_name of the syscall in
    # the action.
    if syscall_name in net_syscall_map:
      syscall_function = net_syscall_map[syscall_name]
    elif syscall_name in fs_syscall_map:
      syscall_function = fs_syscall_map[syscall_name]
    else:
      print "[WARNING] I don't know this system call: ", syscall_name
      continue

    # if the system call has a fd argument, replace the action fd
    # with the model fd.
    if syscall_name in fd_calls:
      if syscall_name == "dup2_syscall":
        # dup2 has two file descriptors. Deal with both.
        model_fd1 = _translate_fd(syscall_args[0])
        model_fd2 = _translate_fd(syscall_args[1])
        # replace both fd with the new ones.
        syscall_args = (model_fd1, model_fd2)
      else:
        model_fd = _translate_fd(syscall_args[0])
        # replace fd in args with the new one.
        syscall_args = (model_fd,) + syscall_args[1:]
      
      # arguments of the action were changed so update the action.
      action = (syscall_name, syscall_args, syscall_return)
    
    model_errno = None
    try:
      mycontext['posix_oracle'].append((syscall_retno, syscall_errno))
      # Execute the system call using the model.
      print "\n"
      print "calling syscall function", syscall_name
      print "with args", syscall_args
      model_retno = syscall_function(*syscall_args)
      

    # If implementation does not implement something so far, make a 
    # note of it and continue
    except UnimplementedError, err:
      print 'UnimplmentedError Not Supported!', err, ' : ', action
      continue

    except SyscallError, err:
      model_retno = -1
      model_errno = err[1]

    # JR: This is a conformance failure, since a POSIX call should 
    # never raise a Repy exception. The Repy model should be
    # transparent to the POSIX model caller.
    except RepyException, err:
      log('ConformanceFailure! RepyException with action: ', action, '\n')
      raise err

    # if model returns that a fd has been ignored, just print relevant
    # information and continue
    except IgnoredFileDescriptorWarning, err:
      print "IGNORING: ", err[1]
      continue


    # There is no way to verify the results. We can only compare the
    # return value of the system call with the one from the model.
    # This is because the model assigns semi-'random' values.
    if (syscall_name in ['fstat_syscall', 'fstatfs_syscall'] and 
        model_retno != -1 and syscall_retno == 0):
      print "OK"

    # Skip file syscalls on files that don't already exist in posix model
    if syscall_name in filepath_calls:
      if model_errno != syscall_errno or model_retno != syscall_retno:
        print "IGNORING: " + str(action) + ". Model returned ", \
              model_errno, model_retno, \
              " which do not match with the implementation."
        continue
    
    # If the file does not exist in the model but it exists on system 
    # (like .so library files), then we should ignore any future
    # references to this fd. Do this by appending the fd in the 
    # ignore_fd list.
    if syscall_name in ['open_syscall', 'creat_syscall']:

      if syscall_errno == None and model_errno != None:
        print "IGNORING:", _short_string(action), \
              ", because model returned an error: ", model_errno

        # EG: I have no other option but to use the ignore_fd here, 
        # because the verifier only should check the return value
        ignore_fd.append(syscall_retno)

        #EG: remove any mapping between model and impl fd, even if the 
        # syscalls fail
        try:
          posix_fd_map.remove(syscall_retno)
        except:
          pass

        continue
    

    # if model returns different fd than the implementation, keep the 
    # correspondance
    # EG: I added dup_syscall
    if (syscall_name in ['socket_syscall', 'open_syscall', 
        'creat_syscall', 'dup_syscall', 'dup2_syscall'] and 
        syscall_retno != -1):
      posix_fd_map[syscall_retno] = model_retno
      model_retno = syscall_retno

    # SS: Examle of accept action:
    # ('accept_syscall', (3,), (4, (['AF_INET'], 50383, '127.0.0.1', 16)))
    # on success the model returns:
    # return remoteip, remoteport, newfd
    if syscall_name  == 'accept_syscall' and syscall_retno != -1:
      # check if ip addrs and ports match
      if (model_retno[0] == syscall_errno[2] and 
          model_retno[1] == syscall_errno[1]):
        posix_fd_map[syscall_retno] = model_retno[2]
        model_retno = syscall_retno
        

    # FS model doesn't need the oracle and a handful of network calls also 
    # don't need it.
    if syscall_name in fs_syscall_map or syscall_name not in oracle_required_funcs:
      mycontext['posix_oracle'].pop()



    # VERIFY RESULTS! 
    # Currently we are just printing them out to visually 
    # verify we are getting something sane.
   
    # many syscalls need special care in order to check if the results from
    # the parser match the results from the model. That is because parser's
    # results are general-purpose and more verbose than we need in this project.


    if (syscall_name == "accept_syscall" and 
        syscall_retno == model_retno and syscall_retno != -1):
      print line_num, "OK:", syscall_name, _short_string(syscall_args), \
            ' -> ', _short_string((syscall_retno, syscall_errno)), "  ", \
            _short_string((model_retno, model_errno))
    
    elif ((syscall_name == 'getpeername_syscall' or 
          syscall_name == 'getsockname_syscall') and
          syscall_errno[1:3] == model_retno):
      # check if port, ip addr match
      # ('getpeername_syscall', (5,), (0, (['AF_INET'], 25588, '127.0.0.1', 16)))
      print line_num, "OK:", syscall_name, _short_string(syscall_args), \
            ' -> ', _short_string((syscall_retno, syscall_errno)), "  ", \
            _short_string((model_retno, model_errno))
    
    elif (syscall_name == 'getsockopt_syscall' and 
          syscall_errno[0] == model_retno):
      # check the value for the option
      # ('getsockopt_syscall', (3, ['SOL_SOCKET'], ['SO_TYPE']), (0, (1, 4)))
      print line_num, "OK:", syscall_name, _short_string(syscall_args), \
            ' -> ', _short_string((syscall_retno, syscall_errno)), "  ", \
            _short_string((model_retno, model_errno))
    
    elif syscall_name == 'read_syscall' and syscall_retno == model_retno:
      print line_num, "OK:", syscall_name, _short_string(syscall_args), \
            ' -> ', _short_string((syscall_retno, syscall_errno)), "  ", \
            _short_string((model_retno, model_errno))
    
    elif syscall_retno != model_retno or syscall_errno != model_errno:
      print (line_num * num), "ERROR:", syscall_name, \
            _short_string(syscall_args), ' -> ', \
            _short_string((syscall_retno, syscall_errno)), "  ", \
            _short_string((model_retno, model_errno))
      ERRORS.append(str(line_num * num) + " ERROR: " + 
                    syscall_name + _short_string(syscall_args) + ' -> ' + 
                    _short_string((syscall_retno, syscall_errno)) + "  " + 
                    _short_string((model_retno, model_errno)))

    else:
      print line_num, " OK: ", syscall_name, _short_string(syscall_args), \
            ' -> ', _short_string((syscall_retno, syscall_errno)), "  ", \
            _short_string((model_retno, model_errno))

  return ERRORS





####################
# Helper Functions #
####################
# Create string that has a max length, this helps when printing large strings.
def _short_string(data, length=800):
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






if __name__ == "__main__":
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
    print _short_string(line)
    fh.write(line + "\n")
    numLines += 1
  fh.write(str(numLines) + " error(s)...\n")
  fh.close()

  print _short_string(numLines) + " error(s)..."
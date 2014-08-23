"""
Main entry point to CheckAPI: verifies function traces against a C API
"""

from parsing.parser_c import *
from framework.checkapi_oracle_setter_getter import *
from model.apr_model_py import *
import framework.checkapi_globals as glob
from framework.checkapi_exceptions import *



class fdtranslator():
  """
  For accessing or updating translations between impl and model fd's
  """

  def __init__(self):
    """
    Initialize fd translation maps
    """
    self.impl_model_fds = {}
    self.model_impl_fds = {}


  def implfd_to_modelfd(self, implfd):
    """
    Given an impl fd, return the model fd equivalent. If none exists, return the
    given impl fd
    """
    try:
      return self.impl_model_fds[implfd]
    except KeyError:
      return implfd


  def modelfd_to_implfd(self, modelfd):
    """
    Given a model fd, return the impl fd equivalent. If none exists, return the
    given model fd
    """
    try:
      return self.model_impl_fds[modelfd]
    except KeyError:
      return modelfd


  def new_translation(self, impl_ret, model_ret, fd_pos):
    """
    If both calls were successful, record the translation between the fd's
    returned by the impl and model, and return True. If either call was
    unsuccessful, return False.
    """
    # Check for non-success in the function return values, always at [-1]
    impl_err = impl_ret[-1] != 0
    model_err = model_ret[-1] != 0

    # Get the return fd's
    impl_fd = impl_ret[fd_pos]
    model_fd = model_ret[fd_pos]

    # Only translate for successful calls
    if impl_err or\
       model_err or\
       impl_fd == glob.NULLINT or\
       model_fd == glob.NULLINT:
      return False

    # Store translations
    self.impl_model_fds[impl_fd] = model_fd
    self.model_impl_fds[model_fd] = impl_fd

    return True



# Function name -> model function
func_map = {"apr_file_open": apr_file_open_model,
            "apr_file_close": apr_file_close_model}

# Functions that require the oracle and the return list index of the relevant
# value
oracle_required_funcs = {}

# Functions with an fd arg or return, and the arg/return list index of that fd
fd_arg_calls = {"apr_file_close": 0}
fd_ret_calls = {"apr_file_open": 0}

# Object for impl and model fd translation
fdtrans = fdtranslator()



def verify_trace(trace):
  """
  Take a list of actions in a trace and execute them in the CheckAPI model,
  reporting any model conformance failures
  """
  errors = []
  line_num = 0

  for action in trace:
    line_num += 1

    # Unpack the action
    func_name, func_args, impl_ret, is_direct = action

    # Get the function based on the name in the action
    if func_name in func_map:
      func = func_map[func_name]
    else:
      print "%d  WARNING:  Unknown function: %s" % (line_num, func_name)
      continue

    func_args_forcall = func_args

    # Replace the action fd with the model fd
    if func_name in fd_arg_calls:
      fd_pos = fd_arg_calls[func_name]

      func_args_forcall = _translate_fd_args(func_name, func_args, fd_pos)

    # Store any required returns in the oracle
    if func_name in oracle_required_funcs:
      oracle_val_pos = oracle_required_funcs[func_name]
      oracle_setter(impl_ret[oracle_val_pos])

    # Nested calls from another API function (not directly from the API user)
    # will also be nested calls made within the model, so don't explicitly call
    # them here
    if not is_direct:
      if glob.debugverify:
        print "%d       Skipping nested call to %s" % (line_num, func_name)
      continue

    # Execute the function using the model
    model_ret = func(*func_args_forcall)

    # Record the translation between the fd's returned by the impl and model
    if func_name in fd_ret_calls:
      fd_pos = fd_ret_calls[func_name]

      if fdtrans.new_translation(impl_ret, model_ret, fd_pos):
        # Replace the model's returned fd with the impl's for verification
        model_ret[fd_pos] = impl_ret[fd_pos]

    # Exceptions don't work properly when the oracle is called from C, so
    # instead, retrieve any stored exception here
    oracle_exception = get_oracle_exception()

    # Handle conformance error in oracle
    if type(oracle_exception) == ModelConformanceFailure:
      result = "%d  ERROR:  %s %s ->  %s" % (line_num, func_name,
               _short_string(func_args), _short_string(str(oracle_exception)))
      # Print error if requested, and store it
      if glob.debugverify:
        print result
      errors.append(result)

      continue

    # Handle internal error in oracle
    elif type(oracle_exception) == InternalCheckAPIError:
      raise oracle_exception

    # No oracle issues, so verify return values
    is_ok = _verify_model_impl_values(func_name, model_ret, impl_ret)

    if glob.debugverify or not is_ok:
      # Construct and print OK or ERROR message
      prefix = "OK" if is_ok else "ERROR"
      result = "%d  %s:  %s %s ->  model: %s   impl: %s" % (line_num, prefix,
               func_name, _short_string(func_args), _short_string(model_ret),
               _short_string(impl_ret))

      # Print ok/error, and store it if error
      print result
      if not is_ok:
        errors.append(result)

  return errors



def _short_string(data, length=800):
  """
  Truncate a string if it exceeds a max length
  """
  data_short = str(data)[:length]

  if len(str(data)) > len(str(data_short)):
    data_short += "!!SHORTENED STRING!!"

  return data_short



def _translate_fd_args(func_name, func_args, fd_pos):
  """
  Translate the implementation's fd into the model's corresponding fd. Return
  the new args
  """
  # Get the impl fd and translate it
  impl_fd = func_args[fd_pos]
  model_fd = fdtrans.implfd_to_modelfd(impl_fd)

  # Replace fd in args with the new one
  new_func_args = list(func_args)
  new_func_args[fd_pos] = model_fd

  # Record translation in args for more informative debug info
  if glob.debugfs:
    func_args[fd_pos] = "%d -> %d" % (impl_fd, model_fd)

  return new_func_args



def _verify_model_impl_values(func_name, model_ret, impl_ret):
  """
  Verify that the implementation's returns match the model's returns
  """
  # For now, all returns should match
  return model_ret == impl_ret



if __name__ == "__main__":
  import argparse

  parser = argparse.ArgumentParser(description="Run the CheckAPI C model to "
    "verify traces")
  parser.add_argument("traces", help="C API traces to verify")
  parser.add_argument("filelist", help="list of files on the implementation's "
    "file system that should exist within the model's")
  parser.add_argument("errors", help="output file to store any errors")
  parser.add_argument("--debugverify", action="store_true", help="print debug "
    "messages during verification")
  parser.add_argument("--debugparse", action="store_true", help="print debug "
    "messages during trace parsing")
  parser.add_argument("--debugfs", action="store_true", help="print debug "
    "messages about the emulated fs and open files state")
  args = parser.parse_args()

  glob.debugverify = args.debugverify
  glob.debugparse = args.debugparse
  glob.debugfs = args.debugfs

  # Get and parse the trace
  trace_file = open(args.traces, "r")
  traces = parse_trace(trace_file)

  # Read in a list of files on the implementation's file system that should
  # already exist in the model's emulated file system
  filelist_file = open(args.filelist, "r")
  fs_readinfilelist(filelist_file)

  # Give the C model pointers to all the python functions it might need to call
  # during verification
  set_py_functions_model()

  # Run CheckAPI
  errors = verify_trace(traces)

  # Write all errors to the error file.
  fh = open(args.errors, "w")
  for line in errors:
    fh.write(line + "\n")
  fh.write(str(len(errors)) + " error(s)\n")
  fh.close()

  print str(len(errors)) + " error(s)"

"""
Main entry point to CheckAPI: verifies function traces against a C API
"""

from parsing.parser_c import *
from framework.checkapi_oracle_setter_getter import *
from model.abccrypto_model_py import *
import framework.checkapi_globals as glob
from framework.checkapi_exceptions import *

# Function name -> model function
func_map = {"get_new_random":get_new_random_model,
            "get_prior_random":get_prior_random_model,
            "file_open":file_open_model}

oracle_required_funcs = ["get_new_random"]

# Functions that have a file descriptor as their first arg or first return
fd_arg_calls = []
fd_ret_calls = ["file_open"]

# Implementation fd -> model fd
fd_map = {}



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
    func_name, func_args, impl_ret = action

    # Get the function based on the name in the action
    if func_name in func_map:
      func = func_map[func_name]
    else:
      print "%d  WARNING:  Unknown function: %s" % (line_num, func_name)
      continue

    # Replace the action fd with the model fd
    if func_name in fd_arg_calls:
      func_args = _translate_fd_args(func_name, func_args)

    # Store the return value in the oracle
    if func_name in oracle_required_funcs:
      # TODO: support all ret args too, not just ret value
      oracle_setter(impl_ret[-1])

    # Execute the function using the model
    model_ret = func(*func_args)

    # Record the translation between the fd's returned by the impl and model
    if func_name in fd_ret_calls:
      _new_fd_translation(impl_ret, model_ret)

    # Exceptions don't work properly when the oracle is called from C, so
    # instead, retrieve any stored exception here
    oracle_exception = get_oracle_exception()

    # Handle conformance error in oracle
    if type(oracle_exception) == ModelConformanceFailure:
      result = "%d  ERROR:  %s %s ->  %s" % (line_num, func_name,
               _short_string(func_args), _short_string(str(oracle_exception)))
      # Print error if requested, and store it
      if glob.debug:
        print result
      errors.append(result)

      continue

    # Handle internal error in oracle
    elif type(oracle_exception) == InternalCheckAPIError:
      raise oracle_exception

    # No oracle issues, so verify return values
    is_ok = _verify_model_impl_values(func_name, model_ret, impl_ret)

    if glob.debug or not is_ok:
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



def _translate_fd_args(func_name, func_args):
  """
  Translate the implementation's fd into the model's corresponding fd. Return
  the new args
  """
  # Impl fd is always the first arg
  impl_fd = func_args[0]

  # Translate impl fd to model fd, or use impl fd if no translation is available
  model_fd = impl_fd
  if impl_fd in fd_map:
    model_fd = fd_map[impl_fd]

  # Replace fd in args with the new one
  return (model_fd,) + func_args[1:]



def _new_fd_translation(impl_ret, model_ret):
  """
  Record the translation between the fd's returned by the impl and model. Modify
  the model's return tuple, with return fd replaced by the impl's return fd
  """
  # Check for errors in the function return values, always at [-1]
  impl_err = impl_ret[-1] < 0
  model_err = model_ret[-1] < 0

  # Only translate for successful calls
  if impl_err or model_err:
    return

  # The return fd is always the first return
  impl_fd = impl_ret[0]
  model_fd = model_ret[0]

  # Store translation
  fd_map[impl_fd] = model_fd

  # Verification would fail erroneously if returns didn't match, so replace
  # the model's returned fd with the impl's returned fd
  model_ret[0] = impl_fd



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
  parser.add_argument("--debug", action="store_true", help="print debug "
    "messages")
  args = parser.parse_args()

  glob.debug = args.debug

  # Get and parse the trace
  trace_file = open(args.traces, "r")
  traces = parse_trace(trace_file)

  # Read in a list of files on the implementation's file system that should
  # already exist in the model's emulated file system
  filelist_file = open(args.filelist, "r")
  fs_readinfilelist(filelist_file)

  # Run CheckAPI
  errors = verify_trace(traces)

  # Write all errors to the error file.
  fh = open(args.errors, "w")
  for line in errors:
    fh.write(line + "\n")
  fh.write(str(len(errors)) + " error(s)\n")
  fh.close()

  print str(len(errors)) + " error(s)"

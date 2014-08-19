"""
Parse and translate traces from a C API into the intermediate representation, as
it is defined in parser_c_intermediate_representation.py. Produces a list of all
parsed trace actions, each action in the form:
  ('funcname', [arg1, arg2, ...], [return1, return2], is_direct)

Node: is_direct indicates a direct call from the API user, not a nested call by
another API call.

Example usage:
  from parsing.parser_c import parse_trace
  fh = open(TRACE_FILE_NAME, "r")
  actions = parse_trace(fh)
"""

from parser_c_intermediate_representation import *
import framework.checkapi_globals as glob
from framework.checkapi_exceptions import *



class UnimplementedError(Exception):
  """
  The parser does not currently implement or support a function found in the
  trace
  """
  pass



def parse_trace(fh):
  """
  Parse and translate traces from a C API into the intermediate representation,
  or a list of actions
  """
  actions = []

  line_num = 0
  line = None

  try:
    # Each iteration parses one action
    while True:
      # Advance line, and skip if blank
      line = fh.next()
      line_num += 1
      if line.strip() == "":
        continue

      # Process return type, func name, and whether the func was called directly
      # by the API user
      #
      # Example trace lines:
      # === int file_write direct
      # === int file_open nested
      (func_rettype, func_name, is_direct) = parse_func_declaration(line,
        line_num)

      # For the func found above, get all arguments, return arguments, and
      # the return value
      #
      # Example trace lines:
      # int 200
      # str_retarg A fine string
      # int_return -1
      arg_list = []
      ret_list = []
      while True:
        # Advance line, and skip if blank
        line = fh.next()
        line_num += 1
        if line.strip() == "":
          continue

        # Parse one line
        (arg, is_retarg, is_ret) = parse_arg_or_ret(line, line_num)

        # Store return args in both lists
        if is_retarg:
          arg_list.append(arg)
          ret_list.append(arg)

        # Store return val
        elif is_ret:
          ret_list.append(arg)

          # Check that the return type is correct
          if not isinstance(arg, func_rettype):
            raise ParseError(("While parsing, %s's expected return type %s was"
              " instead %s") % (func_name, func_rettype, type(arg)))

          # The return val should always be last in a function's trace
          break

        # Store arg
        else:
          arg_list.append(arg)

      if glob.debug:
        print "[parser] %s args: %s return: %s is_direct: %s" % (func_name,
          arg_list, ret_list, str(is_direct))

      # Verify the complete action
      try:
        action = verify_action(func_name, arg_list, ret_list, is_direct)

      # Check for unimplemented functions
      except UnimplementedError:
        if glob.debug:
          print "[WARNING] Function '%s' from trace line %d does not exist in "\
            "the model" % (func_name, line_num)

      # Store action
      else:
        actions.append(action)

  except StopIteration:
    pass

  return actions



def parse_func_declaration(line, line_num):
  """
  Process return type, func name, and whether the func was called directly by
  the API user

  Example trace lines:
  === int file_write direct
  === int file_open nested
  """
  # Split line on whitespace
  split_error = False
  try:
    (tag, rettype_str, func_name, direct_str) = line.split()
  except:
    split_error = True

  # Conversions for func return type and direct call flag
  rettype_flags = {"int": int}
  direct_flags = {"direct": True,
                  "nested": False}

  # Check for malformed line
  if split_error or tag != "===":
    raise ParseError("Log line %d, expected '=== rettype funcname "
      "[direct/nested]', found:\n%s" % (line_num, line))

  # Parse direct flag and func return type
  rettype = rettype_flags[rettype_str]
  is_direct = direct_flags[direct_str]

  return (rettype, func_name, is_direct)



def parse_arg_or_ret(line, line_num):
  """
  Get one argument, return argument, or return value

  Example trace lines:
  int 200
  str_retarg A fine string
  int_return -1
  """
  # Split line on first space
  (arg_type, _, arg) = line.partition(" ")

  # Check for malformed line
  if not arg_type or not arg:
    raise ParseError("Malformed arg or return line, found:\n" + line)

  # Parse arg type
  if arg_type.startswith("int"):
    arg = int(arg)
  elif arg_type.startswith("str"):
    # Remove trailing \n
    arg = arg[:-1]
  else:
    raise ParseError("Log line %d, unknown arg type %s, full line:\n%s" % (
      line_num, arg_type, line))

  # Parse whether it's a return arg, real return value, or neither
  is_ret = is_retarg = False
  if arg_type.endswith("_retarg"):
    is_retarg = True
  elif arg_type.endswith("_return"):
    is_ret = True

  return (arg, is_retarg, is_ret)



def verify_action(func_name, args, ret, is_direct):
  """
  For an action, verify that it has the correct number and type of args and
  return values. Return the packed action
  """
  # Check if function is not implemented in the parser
  if func_name not in HANDLED_FUNCS_INFO:
    raise UnimplementedError()

  # Get expected args and return values from the intermediate representation
  expected_args = HANDLED_FUNCS_INFO[func_name]['args']
  expected_ret = HANDLED_FUNCS_INFO[func_name]['return']

  # Check for the correct number of args and return values
  if len(args) != len(expected_args):
    raise ParseError("For func %s, expected %d args but found %d" % (func_name,
      len(expected_args), len(args)))
  elif len(ret) != len(expected_ret):
    raise ParseError("For func %s, expected %d return values but found %d" % (
      func_name, len(expected_ret), len(ret)))

  # Verify arg types via the intermediate representation
  for i in range(len(expected_args)):
    expected_args[i].check(args[i])

  # Verify return value types via the intermediate representation
  for i in range(len(expected_ret)):
    expected_ret[i].check(ret[i])

  return (func_name, args, ret, is_direct)

"""
Definitions and helpers for converting traces into a consistent intermediate
representation. Each action in this format is of the form:
  ('funcname', [arg1, arg2, ...], [return1, return2])

First, a set of classes defines how to parse each specific type of argument.
Second, a map defines the expected arguments and return values of each supported
function.
"""



class Int():
  """
  Define a primitive int argument
  """

  def check(self, val):
    """
    Check that the argument is a valid int
    """
    if val == None or type(val) != int:
      raise Exception("Argument must be an int, found %s of type %s" %
        (str(val), type(val)))



class Str():
  """
  Define a primitive string argument
  """

  def check(self, val):
    """
    Check that the argument is a valid string
    """
    if val == None or type(val) != str:
      raise Exception("Argument must be a string, found %s of type %s" %
        (str(val), type(val)))



"""
Define the expected arguments and return values of each supported function.
Comments show the implementation's function header, where return arguments are
surrounded by brackets. Arguments and return arguments are always in the same
order as the implementation's function definition and are stored in 'args' and
'return', respectively. The actual function return value is the last element in
'return' after any return arguments.
"""
HANDLED_FUNCS_INFO = {
  # int get_new_random()
  #
  "get_new_random": {
    'args': (),
    'return': (Int(),)
  },

  # int get_prior_random(int index)
  #
  "get_prior_random": {
    'args': (Int(),),
    'return': (Int(),)
  },

  # int file_open([int *fd], char *filename)
  #
  "file_open": {
    'args': (Int(), Str(), Int()),
    'return': (Int(), Int())
  },

  # int file_write(int fd, char *data, [int *nbytes])
  #
  "file_write": {
    'args': (Int(), Str(), Int()),
    'return': (Int(), Int())
  }
}

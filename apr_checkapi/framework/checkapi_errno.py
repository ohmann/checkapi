"""
Errno helpers so that model functions in C and their callbacks in python can
communicate errno values
"""

_errno = 0



def set_errno(new_errno):
  """
  Set the errno value
  """
  global _errno
  _errno = new_errno



def get_errno():
  """
  Get and return the errno value
  """
  return _errno

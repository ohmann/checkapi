'''
Verify observed behavior of the API implementation by storing it and allowing
the model to retrieve it with a condition regex
'''

from framework.checkapi_exceptions import *
import re

# Exceptions don't work properly when called from C [and oracle_getter() always
# is], so instead, store exceptions here, to be accessed with
# get_oracle_exception() and _set_oracle_exception()
_oracle_exception = None

# Implementation values to be verified stored in a stack, to be later popped
# into a map stored as {id -> data}
_oracle_data_raw = []
_oracle_data_by_id = {}
_nextid = 0



def get_oracle_exception():
  """
  Retrieve and clear the stored exception, if any
  """
  tmp = _oracle_exception
  _set_oracle_exception(None)
  return tmp



def _set_oracle_exception(ex):
  """
  Set an exception to be accessed later by verify_c.py
  """
  global _oracle_exception
  _oracle_exception = ex



def _assert_value_okay(cond_regex, value):
  """
  Verify a value with a condition regex, which may be a standard or special
  regex as described in oracle_getter()
  """
  # Locate upper and lower bounds for special regex that is wrapped in < >
  lower, upper = cond_regex.find("<"), cond_regex.rfind(">")

  # Extract special regex
  if lower != -1 and upper != -1:
    special_regex = cond_regex[lower+1:upper]
    leftover_regex = cond_regex[:lower] + cond_regex[upper+1:]

  # No special regex found
  else:
    special_regex = ""
    leftover_regex = cond_regex

  # Process special regex RANGE
  if special_regex.startswith("RANGE"):
    range_min, range_max = special_regex.strip("RANGE").split(",")
    if value < int(range_min) or value > int(range_max):
      raise ModelConformanceFailure("Value '%s' does not match regex ''" %
        (str(value), str(cond_regex)))

  # Process standard regex
  elif special_regex == "":
    # Check value against standard regex
    if not re.search(leftover_regex, str(value)):
      raise ModelConformanceFailure("Value '%s' does not match regex '%s'" %
        (str(value), str(cond_regex)))

  # Malformed regex
  else:
    raise InternalCheckAPIError("Malformed condition regex: " + str(cond_regex))



def oracle_getter(id, cond_regex):
  """
  Verify the implementation's stored return value according to the condition
  regex argument. The id must come from a previous call to oracle_get_id().
  Return the verified value

  Valid regex formats:
  - standard regex, e.g., ".*regex[abc]"
  - special range regex, e.g., "<RANGE 0, 10>" matches range 0 to 10 inclusive
  """
  # Retrieve oracle value by id
  try:
    value = _oracle_data_by_id[id]

  except KeyError:
    # Store the exception
    _set_oracle_exception(InternalCheckAPIError("Attempting to get oracle value"
      " using invalid id: %s" % str(id)))
    return -1

  # Check for None in impl value
  if value == None:
    # Store the exception
    error_str = "'None' value found in stored oracle data"
    _set_oracle_exception(InternalCheckAPIError(error_str))

  # Verify impl value with condition regex, if any
  if cond_regex != None:
    try:
      _assert_value_okay(cond_regex, value)

    # Store the exception, if any
    except Exception as ex:
      _set_oracle_exception(ex)

  # Return impl value
  return value



def oracle_setter(value):
  """
  Store a value in the oracle for later use
  """
  _oracle_data_raw.append(value)



def oracle_get_id():
  """
  Associate the next oracle data with a unique id so that it can be
  unambiguously retrieved later with oracle_getter(). Return the id
  """
  global _nextid

  # Pop the next oracle data, associate it with the next available id
  if not _oracle_data_raw:
    return -1
  _oracle_data_by_id[_nextid] = _oracle_data_raw.pop()

  # Return the unique id to the C caller, and increment
  _nextid += 1
  return _nextid - 1

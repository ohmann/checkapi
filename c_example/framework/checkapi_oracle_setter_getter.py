'''
Verify observed behavior of the API implementation by storing it and allowing
the model to retrieve it with a condition regex
'''

from framework.checkapi_exceptions import *
import re

# Exceptions don't work properly when called from C [and oracle_getter() always
# is], so instead, store exceptions here, to be accessed with
# get_oracle_exception() and set_oracle_exception()
_oracle_exception = None

# Oracle data: a list of function's return values
_oracle_data = []



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
    if not re.search(leftover_regex, value):
      raise ModelConformanceFailure("Value '%s' does not match regex ''" %
        (str(value), str(cond_regex)))

  # Malformed regex
  else:
    raise InternalCheckAPIError("Malformed condition regex: " + str(cond_regex))



def oracle_getter(cond_regex):
  """
  Verify the implementation's stored return value according to the condition
  regex argument. Return the verified value.

  Valid regex formats:
  - standard regex, e.g., ".*regex[abc]"
  - special range regex, e.g., "<RANGE 0, 10>" matches range 0 to 10 inclusive
  """
  # Retrieve prevously-set oracle value, which must exist
  if not _oracle_data:
    _set_oracle_exception(InternalCheckAPIError("Attempting to get oracle value"
      " when none was previously set"))
    return -1
  value = _oracle_data.pop()

  # Check for None in impl value
  if value == None:
    # Store the exception, and verify_c.py will check for it later
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
  _oracle_data.append(value)

"""
Specifies exceptions used throughout CheckAPI
"""

# Exception Definitions
class CheckAPIError(Exception):
  """
  All errors throughout CheckAPI descend from this error
  """
  pass

class ModelConformanceFailure(CheckAPIError):
  """
  There is a conformace failure between impl/model return values
  """
  pass

class InternalCheckAPIError(CheckAPIError):
  """
  An error occurred within the main CheckAPI framework rather during parsing,
  within the model, etc.
  """
  pass

class ParseError(CheckAPIError):
  """
  There is a problem with parsing a trace and we cannot go forward
  """
  pass

class VirtualIOError(CheckAPIError):
  """
  An error occurred within the virtual file system
  """
  pass

class AlreadyExistsError(VirtualIOError):
  """
  A call was made to the virtual file system where a file unexpectedly already
  exists
  """
  pass

class DoesNotExistError(VirtualIOError):
  """
  A call was made to the virtual file system where the referenced file or fd
  does not exist
  """
  pass

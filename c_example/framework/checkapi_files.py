"""
Maintain for the model an instantiated virtual file system (defined in
checkapi_fs.py). Provide functions for the model to open, access, and manipulate
files
"""

import checkapi_globals as glob
from checkapi_fs import *
from framework.checkapi_exceptions import *



class openfd():
  """
  A file descriptor maintaining state for an open file
  """

  def __init__(self, id, inodeid):
    """
    Initialize fd
    """
    self.id = id
    self.inodeid = inodeid
    self.pos = 0


  def seek(self, pos, relative_to=0):
    """
    Seek the current file position relatively or absolutely. Return the new
    position
    """
    self.pos = relative_to + pos
    return self.pos



class filestate():
  """
  The current state of open files (using fds)
  """

  def __init__(self):
    """
    Initialize open files state
    """
    self.nextid = 3
    self.fds = {}


  def create_fd(self, inodeid):
    """
    Create a new fd (i.e., when opening a file). Return the new fd's id
    """
    newfd = openfd(self.nextid, inodeid)
    self.nextid += 1
    return newfd.id



"""
Global variables
"""
std_streams = [0, 1, 2]
filesys = filesystem()
default_dir_mode = 0755
default_file_mode = 0644
fstate = filestate()



def fs_readinfilelist(filelist):
  """
  Read in from a file the list of "files" that should exist in this virtual file
  system
  """

  for line in filelist:
    # Split on whitespace
    tokens = line.strip().split()

    # Lines setting the working dir look like:
    # workingdir = /abs/path/
    if line.startswith("workingdir = "):
      glob.workingdir = tokens[2]

    else:
      path = tokens[0]
      mode = int(tokens[1], 8)

      # Dir lines look like (path ends in / ):
      # ./abs/or/rel/dir/ mode
      if path.endswith("/"):
        filesys.add_dir(path, mode)

      # File lines look like:
      # /abs/or/rel/file mode size
      else:
        size = int(tokens[2])
        filesys.add_file(path, mode, size)

  # For debugging, print the full fs tree
  if glob.debug:
    filesys.print_full_tree()



def fs_open(path, flag, mode=default_file_mode):
  """
  Open a file, potentially creating it. Return the new fd's id or else -1 if
  file can not be opened (or potentially created)
  """

  # Check if file should be created if it doesn't exist
  O_CREAT = 64
  create = flag & 64

  # If requested, try to create the file
  if create:
    try:
      filesys.add_file(path, mode, 0)
    except AlreadyExistsError:
      # File may already exist, which is ok with O_CREAT
      pass
    except Exception:
      return -1

  # Call the virtual fs to open the file
  try:
    inodeid = filesys.open_file(path)
  except DoesNotExistError:
    return -1

  # Add an fd for this file to the open files state
  return fstate.create_fd(inodeid)



def fs_mkdir(path):
  """
  Create a directory
  """
  return -1



def fs_unlink(path):
  """
  Delete a file
  """
  return -1



def fs_rmdir(path):
  """
  Delete a directory
  """
  return -1

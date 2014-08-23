"""
Maintain for the model an instantiated virtual file system (defined in
checkapi_fs.py). Provide functions for the model to open, access, and manipulate
files
"""

import checkapi_globals as glob
from checkapi_fs import *
from framework.checkapi_exceptions import *
from framework.checkapi_files_constants import *
from framework.checkapi_errno import *
from errno import *



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

    """
    OTHER POSSIBLY IMPORTANT ATTRIBUTES, ORIGINALLY SET IN apr_file_open() JUST
    BEFORE RETURNING

    (*new)->flags = flag;
    (*new)->filedes = fd;

    (*new)->blocking = BLK_ON;
    (*new)->buffered = (flag & APR_FOPEN_BUFFERED) > 0;

    if ((*new)->buffered) {
        (*new)->bufsize = APR_FILE_DEFAULT_BUFSIZE;
    }

    (*new)->is_pipe = 0;
    (*new)->timeout = -1;
    (*new)->ungetchar = -1;
    (*new)->eof_hit = 0;
    (*new)->filePtr = 0;
    (*new)->bufpos = 0;
    (*new)->dataRead = 0;
    (*new)->direction = 0;
    """
    self.flags = 0


  def seek(self, pos, relative_to=0):
    """
    Seek the current file position relatively or absolutely. Return the new
    position
    """
    self.pos = relative_to + pos
    return self.pos


  def __repr__(self):
    """
    Pretty-print all open fd fields
    """
    # Translate fd id back to the corresponding impl fd for consistent output
    implfd = modelfd_to_implfd(self.id)

    return "openfd: {id=%d, inodeid=%d, pos=%d}" % (implfd, self.inodeid,
      self.pos)



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
    self.fds[self.nextid] = newfd
    self.nextid += 1
    return newfd.id


  def get_fd(self, implfd_id):
    """
    """
    # Get corresponding model fd id
    modelfd_id = fdtrans.implfd_to_modelfd(implfd_id)

    # Return the actual fd
    try:
      return fds[modelfd_id]
    except KeyError:
      raise DoesNotExistError()


  def remove_fd(self, fd_id):
    """
    Remove an existing fd. Return the removed fd's id or else -1 if the
    specified fd doesn't exist
    """
    try:
      del(self.fds[fd_id])
    except KeyError:
      raise DoesNotExistError()
    return fd_id


  def print_all(self):
    """
    Pretty-print all open fds
    """
    print
    print "[[[ Current open files state ]]]"
    for fd in self.fds.itervalues():
      print "    ", fd
    print



"""
Global variables
"""
std_streams = [0, 1, 2]
filesys = filesystem()
default_dir_mode = 0755
default_file_mode = 0644
fstate = filestate()
fdtrans = fdtranslator()



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
  if glob.debugfs:
    filesys.print_full_tree()



def fs_fcntl(fd_id, cmd, flag=None):
  """
  Manipulate or acess information about a file descriptor. This subset of fcntl
  commands are supported:
  F_GETFD
  F_SETFD
  """
  # Retrieve fd, return -1 if invalid fd_id
  try:
    fd = fstate.get_fd(fd_id)
  except DoesNotExistError:
    set_errno(EBADF)
    return -1

  # Return the fd's flags
  if cmd == F_GETFD:
    return fd.flags

  # Set the fd's flags
  elif cmd == F_SETFD:
    if not flag:
      return -1
    fd.flags = flag
    return 0

  # Invalid command
  else:
    return -1



def fs_open(path, flag, mode=default_file_mode):
  """
  Open a file, potentially creating it. On success, the new fd's id is returned.
  On failure, -1 is returned, and errno is set appropriately
  """
  # If requested, try to create the file
  if flag & O_CREAT:
    try:
      filesys.add_file(path, mode, 0)
    except AlreadyExistsError:
      # The file can already exist with O_CREAT except with O_EXCL
      if flag & O_EXCL:
        set_errno(EEXIST)
        return -1
    except Exception:
      return -1

  # Call the virtual fs to open the file
  try:
    myinode = filesys.open_file(path)
  except DoesNotExistError:
    set_errno(ENOENT)
    return -1

  # Add an fd for this file to the open files state
  ret = fstate.create_fd(myinode.id)

  # For debugging, print the open files state
  if glob.debugfs:
    fstate.print_all()

  return ret



def fs_close(fd_id):
  """
  Close a file. On success, 0 is returned. On failure, -1 is returned, and errno
  is set appropriately
  """
  # Call the virtual fs to close the file
  try:
    fstate.remove_fd(fd_id)
  except DoesNotExistError:
    set_errno(EBADF)
    return -1
  return 0



def fs_mkdir(path):
  """
  Create a directory
  """
  return -1



def fs_unlink(path):
  """
  Delete a file. On success, 0 is returned. On failure, -1 is returned, and
  errno is set appropriately
  """
  # Call the virtual fs to delete the file
  try:
    filesys.del_file(path)
  except DoesNotExistError:
    set_errno(ENOENT)
    return -1
  except VirtualIOError:
    return -1
  return 0



def fs_rmdir(path):
  """
  Delete a directory
  """
  return -1

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



class openfd():
  """
  A file descriptor maintaining state for an open file
  """

  def __init__(self, id, inodeid, fsflags):
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
    self.fsflags = fsflags


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
    return "openfd: {id=%d, inodeid=%d, pos=%d fsflags=%d fdflags=%d}" % (
      self.id, self.inodeid, self.pos, self.fsflags, self.fdflags)



class filestate():
  """
  The current state of open files (using fds)
  """

  def __init__(self):
    """
    Initialize open files state
    """
    self.nextid = 3
    self.fds = {}                   # {fd_id: openfd}
    self.fdflags = {}               # {fd_id: fdflags} for FD_CLOEXEC only


  def _getnextid(self):
    """
    Return the next available fd id
    """
    # Find next available id
    self.nextid += 1
    while self.nextid in fds:
      self.nextid += 1

    return self.nextid


  def create_fd(self, inodeid, fsflags):
    """
    Create a new fd (i.e., when opening a file). Return the new fd's id
    """
    newid = _getnextid()
    newfd = openfd(newid, inodeid, fsflags)
    self.fds[newid] = newfd
    return newid


  def dup_fd(self, oldid, newid=None):
    """
    Duplicate an fd, but always unset fdflags (only FD_CLOEXEC)
    """
    # Get next available fd id if this is dup1
    if not newid:
      newid = _getnextid()

    # Perform the dup
    self.fds[newid] = fds[oldid]
    self.fdflags[newid] = 0

    return newid


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
    fd = fstate.fds[fd_id]
  except KeyError:
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



def fs_dup(oldid):
  """
  Duplicate oldid's fd
  """
  # Check for non-open oldid
  if oldid not in fstate.fds:
    set_errno(EBADF)
    return -1

  # Perform the dup
  return fstate.dup_fd(oldid)



def fs_dup2(oldid, newid):
  """
  Duplicate oldid's fd into newid, which must be a legal but unused fd id
  """
  # Check for non-open oldid, or newid out of valid fd range
  if oldid not in fstate.fds or\
     newid < 0:
    set_errno(EBADF)
    return -1

  if newid in fstate.fds:
    # Do nothing if fds are the same
    if fstate.fds[oldid] == fstate.fds[newid]:
      return newid

    # Close newid
    fstate.remove_fd(newid)

  # Perform the dup
  return fstate.dup_fd(oldid, newid)



def fs_open(path, oflags, mode=default_file_mode):
  """
  Open a file, potentially creating it. On success, the new fd's id is returned.
  On failure, -1 is returned, and errno is set appropriately
  """
  fdflags = 0

  # Set fd flags
  if oflags & O_CLOEXEC:
    fdflags &= FD_CLOEXEC

  # If requested, try to create the file
  if oflags & O_CREAT:
    try:
      filesys.add_file(path, mode, 0)
    except AlreadyExistsError:
      # The file can already exist with O_CREAT except with O_EXCL
      if oflags & O_EXCL:
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
  ret = fstate.create_fd(myinode.id, fdflags)

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

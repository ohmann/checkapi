"""
Define a virtual file system including creation, deletion, and manipulation of
directories, files, and file paths
"""

import os
import checkapi_globals as glob
from framework.checkapi_exceptions import *



def get_std_abs_path(path):
  """
  Create a standardized absolute file path from a relative or absolute path
  """

  # Check for invalid path name
  if not path:
    raise VirtualIOError("Path must be a non-empty str, found: " + str(path))

  # Convert relative paths to absolute
  if not path.startswith("/"):
    path = glob.workingdir + "/" + path

  # Normalize the path ( /A/.//B/../C => /A/C )
  return os.path.normpath(path)



def get_parent_path(path):
  """
  Get a new file path representing the parent of this one (one level up)
  """

  # "/" is its own parent
  if path == "/":
    return path

  # For all other paths, cut off the last dir
  lastdir = path.rindex("/", 0, len(path)-1)

  # Special case if parent is "/", otherwise chop
  if lastdir <= 1:
    parentpath = "/"
  else:
    parentpath = path[:lastdir]
  return parentpath



class inode():
  """
  Generic inode:
  Store inode id, mode, size, and linkcount for a virtual file
  """

  def __init__(self, id, mode, size):
    """
    Initialize generic inode
    """
    self.id = id
    self.mode = mode
    self.size = size
    self.linkcount = 1


  def __repr__(self):
    return "id=%d  mode=%d  size=%d  links=%d" % (self.id, self.mode, self.size,
      self.linkcount)



class fileinode(inode):
  """
  Regular file inode:
  Like a generic inode but also allow adding and deleting paths that reference
  this inode
  """

  def add_path(self):
    """
    Report that a new path references this inode. Return the new linkcount
    """
    self.linkcount += 1
    return self.linkcount


  def del_path(self):
    """
    Report that a path no longer references this inode. Return the new linkcount
    """
    self.linkcount -= 1
    return self.linkcount


  def __repr__(self):
    return "*fileinode* " + inode.__repr__(self)



class dirinode(inode):
  """
  Directory inode:
  Like a generic inode but also allow adding and deleting files and directories
  contained within this one
  """

  def __init__(self, id, mode, parent_id):
    """
    Initialize directory inode
    """
    inode.__init__(self, id, mode, 4096)
    self.contents = {".":id, "..":parent_id}
    self.linkcount = 2


  def add_subfile(self, path, newid):
    """
    Add a file to this directory by the file's existing inode id
    """
    self.__add_content(path, newid)
    return self.linkcount


  def add_subdir(self, path, newid):
    """
    Add a sub-directory to this directory by the sub-directory's existing inode
    id
    """
    # Exactly 1 path points to any dir, so adding an inode id already in this
    # dir's contents is either an error or has no effect
    if newid in self.contents.itervalues():
      raise AlreadyExistsError("Subdir already exists in inode contents: " +
        str(newid))

    # Add the subdir to contents
    self.__add_content(path, newid)
    self.linkcount += 1
    return self.linkcount


  def __add_content(self, path, newid):
    """
    Add a file or directory as being contained within this directory
    """
    # Path must always be unique
    if path in self.contents:
      raise AlreadyExistsError("Subpath dir or file already exists in inode "
        "contents: " + path)
    self.contents[path] = newid


  def __repr__(self):
    return "*dirinode* " + inode.__repr__(self) + "  contents=" + str(self.contents)



class filesystem():
  """
  A virtual file system with stored inodes and paths
  """

  def __init__(self):
    """
    Create a new, empty file system
    """
    # id -> inode obj
    self.idtoinode = {}
    # file path -> inode obj
    self.pathtoinode = {}
    # id for root and next inode to be allocated
    self.rootid = 1
    self.nextid = self.rootid

    # Add root inode
    self.add_dir("/", 0755)


  def add_file(self, path, mode, size):
    """
    Add a regular file to the file system
    """
    # Create standard file path
    path = get_std_abs_path(path)
    if path in self.pathtoinode:
      raise AlreadyExistsError("File already exists: " + str(path))

    # Get its parent path
    parentpath = get_parent_path(path)

    # Parent must exist
    if parentpath not in self.pathtoinode:
      raise VirtualIOError("File parent does not but should already exist for: "
        + str(path))

    # Retrieve parent id
    else:
      parentid = self.pathtoinode[parentpath].id

    # Create new inode obj and store it by id and the current path
    newinode = fileinode(self.nextid, mode, size)
    self.pathtoinode[path] = newinode
    self.idtoinode[self.nextid] = newinode
    self.nextid += 1

    # Update parent inode
    self.pathtoinode[parentpath].add_subfile(path, newinode.id)


  def add_dir(self, path, mode):
    """
    Add a directory to the file system
    """
    # Create standard file path
    path = get_std_abs_path(path)
    if path in self.pathtoinode:
      raise AlreadyExistsError("Directory already exists: " + str(path))

    # Get its parent path
    parentpath = get_parent_path(path)

    # Special case for "/", whose parent inode doesn't exist yet
    if path == "/":
      parentid = self.nextid

    # Otherwise, parent must exist
    elif parentpath not in self.pathtoinode:
      raise VirtualIOError("Directory parent does not but should already exist for: "
        + str(path))

    # Retrieve parent id
    else:
      parentid = self.pathtoinode[parentpath].id

    # Create new inode obj and store it by id and the current path
    newinode = dirinode(self.nextid, mode, parentid)
    self.pathtoinode[path] = newinode
    self.idtoinode[self.nextid] = newinode
    self.nextid += 1

    # Update parent inode
    if path != "/":
      self.pathtoinode[parentpath].add_subdir(path, newinode.id)


  def open_file(self, path):
    """
    Open a file. Return the inode id to which the given path refers
    """
    # Create standard file path
    path = get_std_abs_path(path)

    # Return the inode id
    if path not in self.pathtoinode:
      raise DoesNotExistError("File at path '%s' does not exist" % path)
    return self.pathtoinode[path]


  def get_dir_contents(self, dir):
    """
    Retrieve the contents of a directory. Return two maps, both of the form
    {path -> inode id}, where the first is contained directories and the second
    is contained files within this directory
    """
    dirs = {}
    files = {}

    # For all contents
    for (myname,id) in dir.contents.iteritems():
      myinode = self.idtoinode[id]

      # It's a file
      if isinstance(myinode, fileinode):
        files[myname] = myinode

      # It's a directory
      elif isinstance(myinode, dirinode):
        if myname != "." and myname != "..":
          dirs[myname] = myinode

      else:
        raise VirtualIOError("Inode is neither a regular file nor a directory")
    return (dirs, files)


  def print_full_tree(self):
    """
    Pretty-print the full file system tree of directories and files
    """

    def print_dir(dirname, dir, leading):
      """
      Recursively print the given directory and then its contents
      """
      # Print this dir, and get its contents
      print leading, dirname, " -- ", dir
      (subdirs, files) = self.get_dir_contents(dir)

      # Indent the contents more
      newleading = leading + "  "

      # Subdirs first, print via recursive call to this func
      for (path, myinode) in subdirs.iteritems():
        print_dir(path, myinode, newleading)

      # Files next, print directly
      for (path, myinode) in files.iteritems():
        print newleading, path, " -- ", myinode

    print
    print "[[[ Printing full emulated file system tree ]]]"

    # Get the root inode, and print its full contents
    root = self.idtoinode[self.rootid]
    print_dir("/", root, "")
    print

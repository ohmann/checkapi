"""
<Program>
  generate_lind_fs.py

<Started>
  March 2013

<Author>
  Savvas Savvides

<Purpose>
  This module is responsible for generating a lind file system based on the 
  information gathered from a trace. It provides a single public function which 
  takes as argument a tuple with all the parsed system call actions and creates 
  a set of files that make up the lind file system. The function returns nothing
  
  Example of using this module:

    import generate_lind_fs
    import parser_strace_calls
    
    fh = open(TRACE_FILE_NAME, "r")
    actions = parser_strace_calls.parse_trace(fh)
    generate_lind_fs.generate_fs(actions)

<Remarks>
  generate_fs calls lind_test_server._blank_fs_init() which removes
  all existing lind fs files and initializes the lind.metadata file.
"""

import os
import sys

import lind_test_server
from lind_fs_constants import *

DEBUG = False

"""
This is the only public function of this module. It takes as argument a tuple of
trace actions and generates a lind fs based on the information it can gather 
from these actions and the posix fs.
"""
def generate_fs(actions, trace_path):
  # read the trace and examine the execve syscall to see if the HOME environment
  # variable is set to somewhere else. This usually happens when running 
  # benchmarks. The reason to do this is because actions referring to files 
  # using relative paths, might refere to these files relative to the HOME
  # variable defined in the execve syscall.
  fh = open(trace_path, "r")
  # the execve syscall is the first action of the trace file
  execve_line = fh.readline()
  fh.close()
  
  execve_home_path = None
  if execve_line.find("execve(") != -1:
    execve_parts = execve_line.split(", ")
    # the definition of the HOME variable in the execve syscall has this format:
    # "HOME=/home/savvas/tests/"
    for part in execve_parts:
      if part.startswith("\"HOME="):
        part = part.strip("\"")
        assert(part.startswith("HOME="))
        execve_home_path = part[part.find("HOME=")+5:]

  # load an initial lind file system.
  lind_test_server._blank_fs_init()

  # Keep track of all the file paths dealt with and make a note of
  # whether the file was added to the lind fs or not.
  # Example: {"filename.txt":True, "filename2.txt":False} where True
  # indicates the file was added into the lind fs and False means the
  # file was seen but wasn't added to the lind fs.
  seen_paths = {}

  # a list of system calls that include a filepath in their 
  # arguments.
  syscalls_with_path = ['open', 'creat', 'statfs', 'access', 'stat', 
                        'link', 'unlink', 'chdir', 'rmdir', 'mkdir']
  
  for action in actions:
    # the general format of an action is the following:
    # (syscall_name, (arguments tuple), (return tuple))
    # 
    # Example successful syscall action:
    # ('open_syscall', ('syscalls.txt', ['O_RDONLY', 'O_CREAT'], 
    #    ['S_IWUSR', 'S_IRUSR', 'S_IWGRP', 'S_IRGRP', 'S_IROTH']), 
    #            (3, None))
    #
    # Example unsuccessful syscall action:
    # ('access_syscall', ('/etc/ld.so.nohwcap', ['F_OK']), 
    #                  (-1, 'ENOENT'))
    # ('mkdir_syscall', ('syscalls_dir', ['S_IRWXU', 'S_IRWXG', 
    #        'S_IXOTH', 'S_IROTH']), (-1, 'EEXIST'))
    syscall_name, syscall_parameters, syscall_result = action

    if DEBUG:
      print "Trace:", action

    # each syscall name should end with _syscall
    if not syscall_name.endswith("_syscall"):
      raise Exception("Unexpected name of system call '" + 
                      syscall_name + "'")

    # remove the _syscall part from the syscall name
    syscall_name = syscall_name[:syscall_name.find("_syscall")]

    if syscall_name in syscalls_with_path:

      # TODO: I should consider O_CREAT O_EXECL and O_TRUNC flags.

      # check if the system call is open and whether it includes the O_CREAT 
      # flag.
      o_creat = False
      if syscall_name == "open":
        open_flags = action[1][1]
        if "O_CREAT" in open_flags:
          o_creat = True
      
      # if the system call is creat, again set o_creat to True
      if syscall_name == "creat":
        o_creat = True

      # get the file path from the action
      path = action[1][0]

      # We want the initial file system state. So deal only with the
      # earliest syscall pertaining to a path.
      if path not in seen_paths:
        # if the syscall was successful, copy file/dir into the lind fs.
        if syscall_result != (-1, 'ENOENT'):
          path, path_added = _copy_path_into_lind(path, execve_home_path, o_creat)
          
          # remember this path was seen and whether it was added to the lind fs.
          seen_paths[path] = path_added
        
        else:
          # remember this path was seen but not added to the lind fs.
          seen_paths[path] = False

    # the syscall contains a second path.
    if syscall_name == 'link':
      # ('link_syscall', ('syscalls.txt', 'syscalls.link'), (0, None))
      path2 = action[1][1]

      if path2 not in seen_paths:
        # if we got an exists error, the file must have been there
        # already.
        if syscall_result == (-1, 'EEXIST'):
          path2, path_added = _copy_path_into_lind(path2, execve_home_path, o_creat)
          
          # remember this path was seen and whether it was added to the lind fs.
          seen_paths[path] = path_added
        
        else:
          # remember this path was seen but not added to the lind fs.
          seen_paths[path2] = False

    """
      Can add support for symlink here. A bit more tricky due to return part.
    """
  
  if DEBUG:
    print seen_paths

  # all trace lines are now read. We should confirm that lind fs is as expected.
  all_lind_paths = list_all_lind_paths()

  for seen_path in seen_paths:
    # convert to absolute path.
    abs_seen_path = seen_path
    if not abs_seen_path.startswith("/"):
      abs_seen_path = "/" + abs_seen_path

    if seen_paths[seen_path]:
      # the file should be in lind fs.
      if abs_seen_path not in all_lind_paths:
        raise Exception("Expected file '" + abs_seen_path + 
                        "' not found in Lind fs")
    else:
      # file should not be in lind fs.
      if abs_seen_path in all_lind_paths:
        raise Exception("Unexpected file '" + abs_seen_path + "' in Lind fs")
  

"""
Check if the file/dir exists. Check also in the HOME environment variable as it
is defined in the execve syscall.
If it exists copy it to the lind fs. If not raise an exception.
"""
def _copy_path_into_lind(path, execve_home_path, o_creat):
  if not os.path.exists(path):
    # the file does not exist here. but maybe it exists relative to where the 
    # HOME environment variable points to.
    if execve_home_path != None:
      path = os.path.join(execve_home_path, path)
      
      if not os.path.exists(path):
        # if the O_CREAT flag was set in the system call, allow the program to 
        # proceed even if the file does not exist.
        if o_creat:
          print "[warning] path with O_CREAT not found."
          return path, False
        raise IOError("Cannot locate file on POSIX FS: '" + path + "'")
    else:
      # if the O_CREAT flag was set in the system call, allow the program to 
      # proceed even if the file does not exist.
      if o_creat:
        print "[warning] path with O_CREAT not found."
        return path, False
      raise IOError("Cannot locate file on POSIX FS: '" + path + "'")

  # path exists! Copy it to the lind fs.
  if os.path.isfile(path):
    _cp_file_into_lind(path)
  else:
    _cp_dir_into_lind(path)

  return path, True
  






"""
The rest of this program was adjusted from lind_fs_utils.py

Author: Justin Cappos
Module: File system utilities.   Copies files into the Lind FS from a POSIX
        file system, creates a blank fs, removes files and directories,
        lists files in the fs, etc.

Start Date: Feb 28th, 2012
"""

def _mirror_stat_data(posixfn, lindfn):
  # internal function to take a lind filename (or dirname, etc.) and change
  # it to have similar metadata to a posixfn.   This includes perms, uid, gid

  statdata = os.stat(posixfn)
  
  # I only want the file perms, not things like 'IS_DIR'.  
  # BUG (?): I think this ignores SETUID, SETGID, sticky bit, etc.
  lind_test_server.chmod_syscall(lindfn, S_IRWXA & statdata[0])

  # Note: chown / chgrp aren't implemented!!!   We would call them here.
  #lind_test_server.chown_syscall(lindfn, statdata[4])
  #lind_test_server.chgrp_syscall(lindfn, statdata[5])


def _cp_file_into_lind(fullfilename, rootpath='.', createmissingdirs=True):
  """
   <Purpose>
      Copies a file from POSIX into the Lind FS.   It takes the abs path to 
      the file ('/etc/passwd') and looks for it in the POSIX FS off of the 
      root path.   For example, rootpath = '/foo' -> '/foo/etc/passwd'.
      If the file exists, it is overwritten...

   <Arguments>
      fullfilename: The location the file should live in the Lind FS.  
          This must be an absolute path (from the root).

      rootpath: The directory in the POSIX fs to start looking for that file.
          Note: it must be in the directory structure specified by fullfilename
   
      createmissingdirs:  Should missing dirs in the path be created?

   <Exceptions>
      IOError: If the file does not exist, the directory can't be created
          (for example, if there is a file of the same name), or 
          createmissingdirs is False, but the path is invalid.

   <Side Effects>
      The obvious file IO operations

   <Returns>
      None
  """
  
  # check for the file.
  posixfn = os.path.join(rootpath, fullfilename)

  if not os.path.exists(posixfn):
    raise IOError("Cannot locate file on POSIX FS: '" + posixfn + "'")

  if not os.path.isfile(posixfn):
    raise IOError("POSIX FS path is not a file: '" + posixfn + "'")
  

  # now, we should check / make intermediate dirs if needed...
  # we will walk through the components of the dir and look for them...

  # this removes '.', '///', and similar.   
  # BUG: On Windows, this converts '/' -> '\'.   I don't think lind FS handles
  # '\'...

  normalizedlindfn = os.path.normpath(fullfilename)
  normalizedlinddirname = os.path.dirname(normalizedlindfn)

  # go through the directories and check if they are there, possibly creating
  # needed ones...
  currentdir = ''
  
  # NOT os.path.split!   I want each dir!!!
  for thisdir in normalizedlinddirname.split('/'):
    currentdir += thisdir + '/'

    try:
      # check if this is a directory that exists
      if IS_DIR(lind_test_server.stat_syscall(currentdir)[2]):
        # all is well
        continue
      # otherwise, it exists, but isn't a dir...   
      raise IOError("LIND FS path exists and isn't a dir: '" + currentdir + "'")

    except lind_test_server.SyscallError, e:
      # must be missing dir or else let the caller see this!
      if e[1] != "ENOENT":   
        raise

      # okay, do I create it?
      if not createmissingdirs:
        raise IOError("LIND FS path does not exist but should not be created: '" + currentdir + "'")

      # otherwise, make it ...  
      lind_test_server.mkdir_syscall(currentdir, S_IRWXA)
      # and copy over the perms, etc.
      _mirror_stat_data(os.path.join(rootpath, currentdir), currentdir)


  # Okay, I have made the path now.   Only one thing remains, adding the file
  posixfo = open(posixfn)
  filecontents = posixfo.read()
  posixfo.close()

  # make the new file, truncating any existing contents...
  lindfd = lind_test_server.open_syscall(normalizedlindfn, 
                O_CREAT|O_EXCL|O_TRUNC|O_WRONLY, S_IRWXA)

  # should write all at once...
  datalen = lind_test_server.write_syscall(lindfd, filecontents)
  assert(datalen == len(filecontents))

  lind_test_server.close_syscall(lindfd)

   # fix stat, etc.
  _mirror_stat_data(posixfn, normalizedlindfn)


def _cp_dir_into_lind(fullfilename, rootpath='.', createmissingdirs=True):
  
  # check for the file.
  posixfn = os.path.join(rootpath, fullfilename)

  if not os.path.exists(posixfn):
    raise IOError("Cannot locate dire on POSIX FS: '" + posixfn + "'")

  if os.path.isfile(posixfn):
    raise IOError("POSIX FS path is not a directory: '" + posixfn + "'")
  
  # now, we should check / make intermediate dirs if needed...
  # we will walk through the components of the dir and look for them...

  # this removes '.', '///', and similar.   
  # BUG: On Windows, this converts '/' -> '\'.   I don't think lind FS handles
  # '\'...

  normalizedlindfn = os.path.normpath(fullfilename)

  # go through the directories and check if they are there, possibly creating
  # needed ones...
  currentdir = ''
  
  # NOT os.path.split!   I want each dir!!!
  for thisdir in normalizedlindfn.split('/'):
    currentdir += thisdir + '/'

    try:
      # check if this is a directory that exists
      if IS_DIR(lind_test_server.stat_syscall(currentdir)[2]):
        # all is well
        continue
      # otherwise, it exists, but isn't a dir...   
      raise IOError("LIND FS path exists and isn't a dir: '" + currentdir + "'")

    except lind_test_server.SyscallError, e:
      # must be missing dir or else let the caller see this!
      if e[1] != "ENOENT":   
        raise

      # okay, do I create it?
      if not createmissingdirs:
        raise IOError("LIND FS path does not exist but should not be created: '" + currentdir + "'")

      # otherwise, make it ...  
      lind_test_server.mkdir_syscall(currentdir,S_IRWXA)
      # and copy over the perms, etc.
      _mirror_stat_data(os.path.join(rootpath, currentdir), currentdir)


def list_all_lind_paths(startingdir='/'):
  """
   <Purpose>
      Returns a list of all files / dirs in the lind fs.   Each has an absolute
      name.   This is similar to 'find startingdir'.

   <Arguments>
      startingdir: the path to start with.

   <Exceptions>
      If startingdir is not a dir, this is a SyscallError.

   <Side Effects>
      None

   <Returns>
      A list of strings that correspond to absolute names.   For example:
      ['/','/etc/','/etc/passwd']
  """
  
  # BUG: This code may need to be revisited with symlinks...

  # this will throw exceptions when given bad data...
  lind_test_server.chdir_syscall(startingdir)

  return _find_all_paths_recursively(startingdir)


def _find_all_paths_recursively(startingpath):
  # helper for list_all_lind_paths.   It recursively looks at all child dirs
  
  knownitems = []

  # I need to open the dir to use getdents...
  dirfd = lind_test_server.open_syscall(startingpath,0,0)

  # build a list of all dents.   These have an odd format:
  #  [(inode, filename, d_type (DT_DIR, DR_REG, etc.), length of entry), ...]
  # We only care about the filename and d_type.
  mydentslist = []

  # Note: the length parameter is odd, it's related to data structure space, so
  # it doesn't map to python cleanly.   So long as it's > the largest possible
  # entry size, this code should work though.
  thesedents = lind_test_server.getdents_syscall(dirfd,10000)
  while thesedents:
    mydentslist += thesedents
    thesedents = lind_test_server.getdents_syscall(dirfd,10000)

  lind_test_server.close_syscall(dirfd)

  # to make the output correct, if the dir is '/', don't print it.
  if startingpath == '/':
    startingpath = ''

  for dent in mydentslist:
    # ignore '.' and '..' because they aren't interesting and we don't want
    # to loop forever.
    if dent[1]=='.' or dent[1]=='..':
      continue
   
    thisitem = startingpath+'/'+dent[1]

    # add it...
    knownitems.append(thisitem)

    # if it's a directory, recurse...
    if dent[2]==DT_DIR:
      knownitems = knownitems + _find_all_paths_recursively(thisitem)

  return knownitems
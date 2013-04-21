import os
import sys

import lind_test_server
from lind_fs_constants import *


debug = False

"""
This is the only public function of this module. It takes as argument
a tuple of traces and and generates a lind fs based on the information
it can gather from the traces and the posix fs.
"""
def generate_fs(traces):
  
  for trace in traces:
    # the general form of a trace is as follows:
    # (syscall_name, (arguments tuple), (return tuple))
    syscall_name = trace[0]

    # each syscall name should end with _syscall
    if not syscall_name.endswith("_syscall"):
      raise Exception("Unexpected name of system call when reading " +
                     "trace." + syscall_name)

    # remove the _syscall part from the syscall name
    syscall_name = syscall_name[:syscall_name.find("_syscall")]
    
    # this is a list of some system calls that include a filepath as 
    # in their arguments.
    syscalls_with_path = ['open', 'creat', 'statfs', 'access', 'stat', 
                          'link', 'unlink']
    
    if syscall_name in syscalls_with_path:
      # Example successful syscall trace:
      # ('open_syscall', ('syscalls.txt', ['O_RDONLY', 'O_CREAT'], 
      #    ['S_IWUSR', 'S_IRUSR', 'S_IWGRP', 'S_IRGRP', 'S_IROTH']), 
      #            (3, None))
      #
      # Example unsuccessful syscall trace (file does not exist):
      # ('access_syscall', ('/etc/ld.so.nohwcap', ['F_OK']), 
      #                  (-1, 'ENOENT'))
      
      # get the file path and the syscall result
      path = trace[1][0]
      result = trace[2]
      
      # if the syscall was successful, copy the file.
      if result != (-1, 'ENOENT'):
        _cp_file(path)

    elif syscall_name == "mkdir":
      # ('mkdir_syscall', ('syscalls_dir', ['S_IRWXU', 'S_IRWXG', 
      #        'S_IXOTH', 'S_IROTH']), (-1, 'EEXIST'))
      
      # get the file path and the syscall result
      path = trace[1][0]
      result = trace[2]
      
      # if failure the directory must have been there already
      if result == (-1, 'EEXIST'):
        _cp_dir(path, fs_location)
    
    elif syscall_name == "chdir" or syscall_name == "rmdir":
      # get the directory path and the syscall result
      path = trace[1][0]
      result = trace[2]
      
      # if the syscall was successful, copy the directory.
      if result != (-1, 'ENOENT'):
        _cp_dir(path, fs_location)


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
      lind_test_server.mkdir_syscall(currentdir,S_IRWXA)
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
    raise IOError("Cannot locate file on POSIX FS: '" + posixfn + "'")

  if not os.path.isfile(posixfn):
    raise IOError("POSIX FS path is not a file: '" + posixfn + "'")
  
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
      lind_test_server.mkdir_syscall(currentdir,S_IRWXA)
      # and copy over the perms, etc.
      _mirror_stat_data(os.path.join(rootpath, currentdir), currentdir)
import os
import errno
import shutil

debug = False

"""
This is the only public function of this module. It takes as arguments 
a tuple of traces and a directory location. Then it builds a
filesystem in the given directory location, based to the information 
it gathers from the traces.
"""
def generate_fs(traces, fs_location):
  # get the absolute path for the location where all the files will
  # be copied.
  fs_location = os.path.abspath(fs_location)

  # clear any previous contents.
  if os.path.exists(fs_location):
    shutil.rmtree(fs_location)
  
  # deal with each trace.
  for trace in traces:
    # the general form of a trace is as follows:
    # (syscall_name, (arguments tuple), (return tuple))
    syscall_name = trace[0]

    if not syscall_name.endswith("_syscall"):
      raise Exception("Unexpected name of system call when reading " +
                     "trace." + syscall_name)

    # remove the _syscall part from the syscall name
    syscall_name = syscall_name[:syscall_name.find("_syscall")]
    
    # this is a list of some of the system calls that include a 
    # filepath as one of their arguments.
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
        _cp_file(path, fs_location)

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


def _cp_file(filepath, fs_location):
  # skip directory paths. This can occur in eg open right before 
  # running a getdents syscall
  if os.path.isdir(filepath):
    return

  filepath = os.path.normpath(filepath)
  filedir = os.path.dirname(filepath)
  
  # is the filepath an absolute path or a relative one?
  # construct the new filepath accordingly.
  if filepath.startswith("/"):
    newfilepath = fs_location + filepath
  else:
    newfilepath = fs_location + "/" + filepath
  
  # if the new file is already there do nothing.
  if os.path.exists(newfilepath):
    return

  if os.path.exists(filepath):
    # go through all directories and create the ones missing
    currentdir = ''
    for thisdir in filedir.split('/'):
      currentdir += thisdir + '/'
      newdir = fs_location + currentdir

      # if the directory does not exist, create it.
      if not os.path.isdir(newdir):
        if os.path.isfile(newdir):
          raise IOError("path exists and isn't a dir: " + currentdir)
        os.makedirs(newdir)

      # copy directory stats
      # If I do this it prevents some files from being copied.
      # shutil.copystat(currentdir, newdir) 

    # now copy the file
    shutil.copy2(filepath, newfilepath)

  else:
    # if the file does not exist create a dummy version of it.
    if debug:
      print "File not found, creating empty file."

    # create the missing directories.
    newfiledir = os.path.dirname(newfilepath)
    try:
      os.makedirs(newfiledir)
    except OSError as exc:
      if exc.errno == errno.EEXIST and os.path.isdir(newfiledir):
        pass
      else:
        raise

    # create an empty file.
    open(newfilepath, 'a').close()



def _rm_file(filepath, fs_location):
  print "filepath", filepath
  
  # skip directory paths.
  if os.path.isdir(filepath):
    return

  filepath = os.path.normpath(filepath)
  
  if filepath.startswith("/"):
    newfilepath = fs_location + filepath
  else:
    newfilepath = fs_location + "/" + filepath
  
  if os.path.exists(newfilepath):
    os.unlink(newfilepath)


def _cp_dir(dirpath, fs_location):
  if not dirpath.endswith("/"):
    dirpath += "/"
  
  dirpath = os.path.normpath(dirpath)
  
  if dirpath.startswith("/"):
    newdirpath = fs_location + dirpath
  else:
    newdirpath = fs_location + "/" + dirpath

  # if the new dir is already there do nothing.
  if os.path.exists(newdirpath):
    return

  if os.path.exists(dirpath):
    # go through all directories and create the ones missing
    currentdir = ''
    for thisdir in dirpath.split('/'):
      currentdir += thisdir + '/'
      newdir = fs_location + currentdir

      # if the directory does not exist, create it.
      if not os.path.isdir(newdir):
        if os.path.isfile(newdir):
          raise IOError("path exists and isn't a dir: " + currentdir)
        os.makedirs(newdir)
      
      # copy directory stats
      # shutil.copystat(currentdir, newdir)
  else:
    # if the file does not exist create a dummy version of it.
    if debug:
      print "Directory not found, creating new."
    
    # create the missing directories.
    try:
      os.makedirs(newdirpath)
    except OSError as exc:
      if exc.errno == errno.EEXIST and os.path.isdir(newdirpath):
        pass
      else:
        raise


def _rm_dir(dirpath, fs_location):
  if not dirpath.endswith("/"):
    dirpath += "/"

  dirpath = os.path.normpath(dirpath)
  
  if dirpath.startswith("/"):
    newdirpath = fs_location + dirpath
  else:
    newdirpath = fs_location + "/" + dirpath
  
  if os.path.exists(newdirpath):
    shutil.rmtree(newdirpath)
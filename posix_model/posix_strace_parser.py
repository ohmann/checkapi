####################################################
# Classes that define the expected format and type #
# of arguments and return values of system calls.  #
####################################################
class Skip():
  """Indicates skip argument."""
  def __init__(self, output=None):
    self.output = output

class SkipRemaining():
  """Indicates skip all remaining arguments."""
  def __init__(self, output=None):
    self.output = output


class Int():
  """Parses int."""
  def __init__(self, output=None):
    self.output = output

  def parse(self, val):
    # dereferenced numbers are wrapped in []
    if val.startswith('[') and val.endswith(']'):
      val = val[1:-1]

    # some numbers are followed by a comment inside /* */
    # eg shutdown syscall.
    if val.find('/*') != -1 and val.find('*/') != -1:
      val = val[:val.find('/*')].strip()

    try:
      val = int(val)
    except:
      raise Exception("Unexpected format when parsing type: %s" %
                       type(val))
    return val


class Str():
  """Parses str or unicode."""
  def __init__(self, output=None):
    self.output = output
 
  def parse(self, val):
    if not (type(val) is str or type(val) is unicode):
      raise Exception("Unexpected format when parsing type: %s" %
                       type(val))

    if val.endswith('\"...'):
      val = val[:val.rfind('...')]
    # strace always wraps strings in double quotes.
    if not val.startswith('\"') or not val.endswith('\"'):
      raise Exception("Unexpected format when parsing type: %s" %
                       type(val))
    # remove double quotes.
    val = val[1:-1]
    # replace special characters.
    val = val.replace("\\n", "\n")
    val = val.replace("\\r", "\r")
    val = val.replace("\\t", "\t")
    val = val.replace("\\0", "\0")
    return val


class ListOfStr():
  """Parses list of strings."""
  def __init__(self, output=None):
    self.output = output

  def parse(self, val):
    return val.split("|")


class Mode():
  """Parses mode_t. Translates number or list of flags."""
  def __init__(self, output=None):
    self.output = output

  def parse(self, val):
    try:
      val = int(val)
    except:
      raise Exception("Unexpected format when parsing type: %s" %
                       type(val))
    return numToListOfFlags(val)


class IntOrListOfStr():
  """Parses int or list of strings."""
  def __init__(self, output=None):
    self.output = output

  def parse(self, val):
    try:
      val = int(val)
    except:
      val = val.split("|")
    return val


class IntOrQuestionOrListOfStr():
  """Parses int or question mark or list of strings
  
  int covers most cases
  queston mark appears in some rare cases eg in exit_group
  
  ListOfStr appears only in fcntl which returns a hex followed by a
  set of flags.
  """
  def __init__(self, output=None):
    self.output = output

  def parse(self, val):
    try:
      val = int(val)
    except:
      if val == '?':
        return val
      return val.split("|")
    return val


class NoneOrStr():
  """Parses a NoneType or a string."""
  def __init__(self, output=None):
    self.output = output
 
  def parse(self, val):
    if val is not None and not (type(val) is str or type(val) is unicode):
      raise Exception("Unexpected format when parsing type: %s" %
                       type(val))
    return val


class SockFamily():
  """Parses sa_family of struct sockaddr."""
  def __init__(self, output=None):
    self.output = output

  def parse(self, val):
    if val.find('sa_family=') == -1:
      raise Exception("Unexpected format when parsing type: %s" %
                       type(val))
    val = val[val.find('sa_family=')+len('sa_family='):]
    return val.split("|")


class SockIP():
  """Parses sin_addr of struct sockaddr."""
  def __init__(self, output=None):
    self.output = output

  def parse(self, val):
    # IP is given in the format 'inet_addr("A.B.C.D")'
    if val.find('inet_addr(\"') == -1 or val.find('\")') == -1:
      raise Exception("Unexpected format when parsing type: %s" %
                       type(val))
    val = val[val.find('inet_addr(\"')+len('inet_addr(\"'):val.rfind('\")')]
    return val


class SockPort():
  """Parses sin_port of struct sockaddr."""
  def __init__(self, output=None):
    self.output = output

  def parse(self, val):
    # Port is given in the format 'htons(#####)'
    if val.find('htons(') == -1 or val.find(')') == -1:
      raise Exception("Unexpected format when parsing type: %s" %
                       type(val))
    try:
      val = int(val[val.find('htons(')+len('htons('):val.find(')')])
    except:
      raise Exception("Unexpected format when parsing type: %s" %
                       type(val))
    return val


class StMode():
  """Parses st_mode of struct stat."""
  def __init__(self, output=None):
    self.output = output

  def parse(self, val):
    if val.find('st_mode=') == -1:
      # if the syscall had an error the address of the struct is 
      # returned instead.
      if val.startswith('0x'):
        return MISSING_VALUE
      raise Exception("Invalid type %s" % val)
    val = val[val.find('st_mode=')+len('st_mode='):]
    return val.split("|")


class StSize():
  """Parses st_size of struct stat."""
  def __init__(self, output=None):
    self.output = output

  def parse(self, val):
    if val.find('st_size=') == -1:
      raise Exception("Unexpected format when parsing type: %s" %
                       type(val))
    try:
      val = int(val[val.find('st_size=')+len('st_size='):])
    except:
      raise Exception("Unexpected format when parsing type: %s" %
                       type(val))
    return val


"""
Information about individual system calls.
The declaration of each syscall is provided in comments followed by
one or more examples of strace output for that syscall.
The strace general output format is as follows:
pid syscall_name(args) = return

These information are used for parsing and translating strace output
to the intermediate representation.
The general format of the intermediate representation is:
('syscallName_syscall', (args1, arg2, ...), (return1, return2, ...))
where the order of args and return values is the same as the order
they appear in the strace output.

Each syscall has a set of arguments and return values associated with
it. Each argument or return value is represented by a class, which
defines its expected format when parsing it, and its expected type
when translating it to the intermediate representation. These classes
can optionally take an argument "output=True" which indicates that the
current argument is used to return a value rather than to pass a
value, and hence the argument should be moved in the return part of
the intermediate representation.
"""
HANDLED_SYSCALLS_INFO = {
  # int socket(int domain, int type, int protocol);
  # 
  # Example strace output:
  # 19176 socket(PF_INET, SOCK_STREAM, IPPROTO_IP) = 3
  # 19294 socket(PF_INET, SOCK_DGRAM, IPPROTO_UDP) = 3
  "socket": {
    'args': (ListOfStr(), ListOfStr(), ListOfStr()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int bind(int sockfd, const struct sockaddr *addr, socklen_t addrlen);
  # 
  # Example strace output:
  # 19176 bind(3, {sa_family=AF_INET, sin_port=htons(25588), sin_addr=inet_addr("127.0.0.1")}, 16) = 0
  # 19184 bind(3, {sa_family=AF_INET, sin_port=htons(25588), sin_addr=inet_addr("127.0.0.1")}, 16) = -1 EADDRINUSE (Address already in use)
  "bind": {
    'args': (Int(), SockFamily(), SockPort(), SockIP(), Int()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen);
  # 
  # Example strace output:
  # 19175 connect(5, {sa_family=AF_INET, sin_port=htons(25588), sin_addr=inet_addr("127.0.0.1")}, 16) = 0
  # 19262 connect(5, {sa_family=AF_INET, sin_port=htons(25588), sin_addr=inet_addr("127.0.0.1")}, 16) = -1 ECONNREFUSED (Connection refused)
  "connect": {
    'args': (Int(), SockFamily(), SockPort(), SockIP(), Int()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # ssize_t sendto(int sockfd, const void *buf, size_t len, int flags, const struct sockaddr *dest_addr, socklen_t addrlen);
  # 
  # Example strace output:
  # 19309 sendto(3, "Message for sendto.\0", 20, 0, {sa_family=AF_INET, sin_port=htons(25588), sin_addr=inet_addr("127.0.0.1")}, 16) = 20
  "sendto": {
    'args': (Int(), Str(), Int(), IntOrListOfStr(), SockFamily(), 
             SockPort(), SockIP(), Int()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # ssize_t send(int sockfd, const void *buf, size_t len, int flags);
  # 
  # Example strace output:
  # 19285 send(4, "Message to be received.\0", 24, 0) = 24
  # 19304 send(5, "\0\0c\364", 4, 0)        = -1 EPIPE (Broken pipe)
  "send": {
    'args': (Int(), Str(), Int(), IntOrListOfStr()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # ssize_t recvfrom(int sockfd, void *buf, size_t len, int flags, struct sockaddr *src_addr, socklen_t *addrlen);
  # 
  # Example strace output:
  # 19294 recvfrom(3, "Message for sendto.\0", 512, 0, {sa_family=AF_INET, sin_port=htons(40299), sin_addr=inet_addr("127.0.0.1")}, [16]) = 20
  "recvfrom": {
    'args': (Int(), Str(output=True), Int(), IntOrListOfStr(), SockFamily(output=True), 
             SockPort(output=True), SockIP(output=True), Int(output=True)),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # ssize_t recv(int sockfd, void *buf, size_t len, int flags);
  # 
  # Example strace output:
  # 19284 recv(5, "Message to be received.\0", 24, 0) = 24
  "recv": {
    'args': (Int(), Str(output=True), Int(), IntOrListOfStr()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int getsockname(int sockfd, struct sockaddr *addr, socklen_t *addrlen);
  # 
  # Example strace output:
  # 19255 getsockname(3, {sa_family=AF_INET, sin_port=htons(0), sin_addr=inet_addr("0.0.0.0")}, [16]) = 0
  "getsockname": {
    'args': (Int(), SockFamily(output=True), SockPort(output=True), SockIP(output=True), Int(output=True)),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int   getpeername(int sockfd, struct sockaddr *addr, socklen_t *addrlen);
  # 
  # Example strace output:
  # 19252 getpeername(5, {sa_family=AF_INET, sin_port=htons(25588), sin_addr=inet_addr("127.0.0.1")}, [16]) = 0
  "getpeername": {
    'args': (Int(), SockFamily(output=True), SockPort(output=True), SockIP(output=True), Int(output=True)),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int listen(int sockfd, int backlog);
  # 
  # Example strace output:
  # 19176 listen(3, 5) = 0
  "listen": {
    'args': (Int(), Int()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int accept(int sockfd, struct sockaddr *addr, socklen_t *addrlen);
  # 
  # Example strace output:
  # 19176 accept(3, {sa_family=AF_INET, sin_port=htons(42572), sin_addr=inet_addr("127.0.0.1")}, [16]) = 4
  "accept": {
    'args': (Int(), SockFamily(output=True), SockPort(output=True), SockIP(output=True), Int(output=True)),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int getsockopt(int sockfd, int level, int optname, void *optval, socklen_t *optlen);
  # 
  # Example strace output:
  # 19258 getsockopt(3, SOL_SOCKET, SO_TYPE, [1], [4]) = 0
  # 19258 getsockopt(3, SOL_SOCKET, SO_OOBINLINE, [0], [4]) = 0
  "getsockopt": {
    'args': (Int(), IntOrListOfStr(), IntOrListOfStr(), Int(output=True), Int(output=True)),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int setsockopt(int sockfd, int level, int optname, void *optval, socklen_t optlen);
  # 
  # Example strace output:
  # 19313 setsockopt(3, SOL_SOCKET, SO_REUSEADDR, [1], 4) = 0
  "setsockopt": {
    'args': (Int(), IntOrListOfStr(), IntOrListOfStr(), Int(), Int()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int shutdown(int sockfd, int how);
  # 
  # Example strace output:
  # 19316 shutdown(5, 0 /* receive */) = 0
  # 19316 shutdown(5, 2 /* send and receive */) = 0
  "shutdown": {
    'args': (Int(), Int()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int close(int fd);
  # 
  # Example strace output:
  # 19319 close(3) = 0
  "close": {
    'args': (Int(), Int()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int fstatfs(int fd, struct statfs *buf);
  # 
  # Example strace output:
  # 19243 fstatfs(3, {f_type="EXT2_SUPER_MAGIC", f_bsize=4096, f_blocks=4553183, f_bfree=1457902, f_bavail=1226606, f_files=1158720, f_ffree=658673, f_fsid={-1853641883, -1823071587}, f_namelen=255, f_frsize=4096}) = 0
  "fstatfs": {
    'args': (Int(), SkipRemaining()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int statfs(const char *path, struct statfs *buf);
  # 
  # Example strace output:
  # 19323 statfs("syscalls.txt", {f_type="EXT2_SUPER_MAGIC", f_bsize=4096, f_blocks=4553183, f_bfree=1458896, f_bavail=1227600, f_files=1158720, f_ffree=658713, f_fsid={-1853641883, -1823071587}, f_namelen=255, f_frsize=4096}) = 0
  "statfs": {
    'args': (Str(), SkipRemaining()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int access(const char *pathname, int mode);
  # 
  # Example strace output:
  # 19178 access("syscalls.txt", F_OK) = 0
  # 19178 access("syscalls.txt", R_OK|W_OK) = 0
  # 19178 access("syscalls.txt", X_OK) = -1 EACCES (Permission denied)
  "access": {
    'args': (Str(), IntOrListOfStr()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int chdir(const char *path);
  # 
  # Example strace output:
  # 19217 chdir(".") = 0
  "chdir": {
    'args': (Str(),),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int mkdir(const char *pathname, mode_t mode);
  # 
  # Example strace output:
  # 19269 mkdir("syscalls_dir", 0775) = -1 EEXIST (File exists)
  "mkdir": {
    'args': (Str(), Mode()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int rmdir(const char *pathname);
  # 
  # Example strace output:
  # 19302 rmdir("syscalls_dir") = 0
  "rmdir": {
    'args': (Str(),),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int link(const char *oldpath, const char *newpath);
  # 
  # Example strace output:
  # 19260 link("syscalls.txt", "syscalls.link") = -1 EEXIST (File exists)
  # 19260 link("hopefully_no_such_filename_exists.txt", "syscalls2.link") = -1 ENOENT (No such file or directory)
  "link": {
    'args': (Str(), Str()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int symlink(const char *oldpath, const char *newpath);
  # 
  # Example strace output:
  # 19267 symlink("syscalls.txt", "syscalls.symlink") = 0
  "symlink": {
    'args': (Str(), Str()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int unlink(const char *pathname);
  # 
  # Example strace output:
  # 19327 unlink("syscalls.txt") = 0
  # 19327 unlink("syscalls.symlink")        = 0
  # 19327 unlink("hopefully_no_such_filename_exists.txt") = -1 ENOENT (No such file or directory)
  "unlink": {
    'args': (Str(),),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int stat(const char *path, struct stat *buf);
  # 
  # Example strace output:
  # 19321 stat64("syscalls.txt", {st_mode=S_IFREG|0664, st_size=45, ...}) = 0
  # 19321 stat64("hopefully_no_such_filename_exists.txt", 0xbf8c7d50) = -1 ENOENT (No such file or directory)
  "stat": {
    'args': (Str(), StMode(output=True), StSize(output=True), Skip()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int fstat(int fd, struct stat *buf);
  # 
  # Example strace output:
  # 19175 fstat64(3, {st_mode=S_IFREG|0644, st_size=98710, ...}) = 0
  # 19175 fstat64(3, {st_mode=S_IFREG|0755, st_size=124663, ...}) = 0
  "fstat": {
    'args': (Int(), StMode(output=True), StSize(output=True), Skip()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int open(const char *pathname, int flags);
  # int open(const char *pathname, int flags, mode_t mode);
  # 
  # Example strace output:
  # 19224 open("syscalls.txt", O_RDONLY|O_CREAT, 0664) = 3
  # 19224 open("syscalls2.txt", O_RDWR|O_CREAT|O_APPEND, 0664) = 3
  "open": {
    'args': (Str(), IntOrListOfStr(), Mode()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int creat(const char *pathname, mode_t mode);
  # 
  # Example strace output:
  # 19229 creat("syscalls.txt", 0666)       = 3
  # 19229 creat("syscalls2.txt", 0600)      = 4
  "creat": {
    'args': (Str(), Mode()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # off_t lseek(int fd, off_t offset, int whence);
  # 
  # Example strace output:
  # 19265 lseek(3, 1, SEEK_SET) = 1
  # 19265 lseek(3, 5, SEEK_CUR) = 16
  "lseek": {
    'args': (Int(), Int(), IntOrListOfStr()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # ssize_t read(int fd, void *buf, size_t count);
  # 
  # Example strace output:
  # 19282 read(3, "abcdefghijklmnopqrst", 20) = 20
  "read": {
    'args': (Int(), Str(output=True), Int()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # ssize_t write(int fd, const void *buf, size_t count);
  # 
  # Example strace output:
  # 19265 write(3, "abcdefghijklmnopqrstuvwxyz", 26) = 26
  "write": {
    'args': (Int(), Str(), Int()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int dup(int oldfd);
  # 
  # Example strace output:
  # 19231 dup(3) = 4
  # 19231 dup(3) = -1 EBADF (Bad file descriptor)
  "dup": {
    'args': (Int(),),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int dup2(int oldfd, int newfd);
  # 
  # Example strace output:
  # 19233 dup2(3, 4) = 4
  # 19233 dup2(3, 3) = 3
  # 19233 dup2(3, -1) = -1 EBADF (Bad file descriptor)
  "dup2": {
    'args': (Int(), Int()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int dup3(int oldfd, int newfd, int flags);
  # 
  # Example strace output:
  # 19235 dup3(3, 4, O_CLOEXEC) = 4
  "dup3": {
    'args': (Int(), Int(), IntOrListOfStr()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int getdents(unsigned int fd, struct linux_dirent *dirp, unsigned int count);
  # 
  # Example strace output:
  # 19249 getdents(3, /* 41 entries */, 1024) = 1016
  # 19249 getdents(3, /* 7 entries */, 1024) = 200
  # 19249 getdents(3, /* 0 entries */, 1024) = 0
  "getdents": {
    'args': (Int(), Skip(), Int()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int fcntl(int fd, int cmd, ... /* arg */ );
  # 
  # Example strace output:
  # 19239 fcntl64(3, F_GETFL) = 0 (flags O_RDONLY)
  # 19239 fcntl64(4, F_GETFL) = 0x402 (flags O_RDWR|O_APPEND)
  "fcntl": {
    'args': (Int(), IntOrListOfStr(), IntOrListOfStr()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  }
}

#############
# CONSTANTS #
#############
FILE_NAME = "all.strace" # input file
UNIMPLEMENTED_ERROR = -1
MISSING_VALUE = -2
SIGS = ["---", "+++"]
DEBUG = True


###########
# STRUCTS #
###########
class UnfinishedSyscall(object):
  def __init__(self, pid, command, firstHalf):
    self.pid = pid
    self.command = command
    self.firstHalf = firstHalf

  def __str__(self):
    line = str([self.pid, self.command, self.firstHalf])
    return line

SKIPPED_SYSCALLS = {}


###################################
# Public function of this module. #
###################################
def getTraces(fh):
  TRACES = []
  unfinished_syscall = []
  
  # process each line
  for line in fh:
    line = line.strip()
    
    if DEBUG:
      log(line, "\n")
        
    # Ignore SIGS
    if line[:3] in SIGS:
      if DEBUG:
        log("Ignoring SIG.")
      continue

    # Did the strace get interrupted?
    if line.find("<unfinished ...>") != -1:
      # Ignore lines with only unfinished
      if line != "<unfinished ...>":
        saveUnfinishedSyscall(line, unfinished_syscall)
      continue

    # Is the strace resuming?
    if line.find("<... ") != -1 and line.find(" resumed>") != -1:
      line = resumeUnfinishedSyscall(line, unfinished_syscall)
      if line == -1: # unfinished syscall not found
        continue
      

    # Ignore lines starting with Process:
    if line[:line.find(" ")] == "Process":
      if DEBUG:
        log("Skipping Process line.")
      continue
    
    # Ignore incomplete strace lines without '(', ')', and '='
    if line.find('(') == -1 or line.find(')') == -1 or line.find('=') == -1:
      if DEBUG:
        log("Skipping Incomplete line.")
      continue
    
    # Get the command name.
    if line[0] == '[':
      command = line[line.find(']')+2:line.find('(')]
    elif len(line[:line.find('(')].split(" ")) > 1:
      command = line[:line.find('(')].split(" ")[-1]
    else:
      command = line[:line.find('(')]
    
    # Get the function parameters.
    parameterChunk = line[line.find('(')+1:line.rfind('=')].strip()
    parameters = parameterChunk[:-1].split(", ")
    
    # Get the result.
    straceResult = line[line.rfind('=')+1:].strip()
    if straceResult.find("(flags ") != -1:
      # handle fcntl return part.
      straceResult = straceResult[straceResult.find("(flags ") +
                     len("(flags "):straceResult.rfind(")")]
      straceResult = (straceResult, None)
    else:
      spaced_results = straceResult.split(" ")
      if len(spaced_results) > 1:
        straceResult = straceResult[:straceResult.find(" ")]
      try: 
        straceResult = int(straceResult) # result can also be a '?'
      except:
        pass
      if straceResult == -1 and len(spaced_results) > 1:
        straceResult = (straceResult, spaced_results[1])
      else:
        straceResult = (straceResult, None)

    trace = process_trace(command, parameters, straceResult)
    
    if trace != UNIMPLEMENTED_ERROR:
      TRACES.append(trace)
  
  # display all skipped commands.
  log("\n\nSkipped System Calls\n")
  for skipped in SKIPPED_SYSCALLS:
    log(skipped + ": " + str(SKIPPED_SYSCALLS[skipped]) + "\n")
  log("\n")

  return TRACES



# parses each argument according to what's expected for that syscall
# and translates to the intermediate representation.
def process_trace(command, args, result):
  if command.endswith('64'):
    command = command[:command.rfind('64')]

  if command not in HANDLED_SYSCALLS_INFO:
    # keep track of how many times each syscall was skipped.
    if(command in SKIPPED_SYSCALLS):
      SKIPPED_SYSCALLS[command] = SKIPPED_SYSCALLS[command] + 1;
    else:
      SKIPPED_SYSCALLS[command] = 1;
    return UNIMPLEMENTED_ERROR

  expected_args = HANDLED_SYSCALLS_INFO[command]['args']
  args_tuple = ()
  expected_return = HANDLED_SYSCALLS_INFO[command]['return']
  return_tuple = ()
  
  # Parse the individual arguments of the syscall.
  #
  # Length of args can change. If the syscall containes a string and
  # the string containes ", " the parser will wrongly split the
  # string.
  index = 0
  while index < len(args):
    # Do we have more than the expected arguments?
    if index >= len(expected_args):
      raise Exception("Unexpected argument.")
    
    expected_arg_type = expected_args[index]
    # Skip all remaining arguments?
    if isinstance(expected_arg_type, SkipRemaining):
      break
    # Skip this argument?
    if isinstance(expected_arg_type, Skip):
      index += 1
      continue

    # Did the string contain ", "?
    if isinstance(expected_arg_type, Str):
      # if the length of arguments is bigger than the length of the
      # expected arguments then we either intentionally skip some
      # arguments or the string was wrongly split.
      last_arg_type = expected_args[-1]
      if (len(args) > len(expected_args) and not 
             isinstance(last_arg_type, SkipRemaining)):
        end = len(args) - len(expected_args) + index
        for i in range(index, end):
          args[index] += ", " + args[index+1]
          args.pop(index+1)

    argument = expected_arg_type.parse(args[index])
    
    # Did the syscall return an error?
    if isinstance(expected_arg_type, StMode):
      if argument == MISSING_VALUE:
        break
    
    # Is the argument a return value rather than an argument?
    if expected_arg_type.output:
      return_tuple = return_tuple + (argument,)
    else:
      args_tuple = args_tuple + (argument,)

    index += 1
  
  # parse the return values of the syscall
  for index in range(len(result)):
    expected_return_type = expected_return[index]
    return_argument = expected_return_type.parse(result[index])
    return_tuple = return_tuple + (return_argument,)
  
  # form the intermediate representation.
  trace = (command+'_syscall', args_tuple, return_tuple)
  return trace


#####################
# Helper Functions. #
#####################
def saveUnfinishedSyscall(line, unfinished_syscall):
  try:
    pid = int(line[line.find(" ")+1:line.find("]")])
    command = line[line.find("]")+1:line.find("(")].strip()
  except:
    pid = int(line[:line.find(" ")])
    command = line[line.find(" ")+1:line.find("(")].strip()
  if command in HANDLED_SYSCALLS_INFO:
    #return [(pid, command)]
    unfinished_syscall.append(UnfinishedSyscall(pid, command, line[:line.find("<unfinished ...>")].strip()))
    if DEBUG:
      log("Unfinished syscall saved.\n\n")
  else:
    if DEBUG:
      log("Skipping unimplimented unfinished syscall.\n\n")
    

def resumeUnfinishedSyscall(line, unfinished_syscall):
  try:
    pid = int(line[line.find(" ")+1:line.find("]")])
  except:
    pid = int(line[:line.find(" ")])
  command = line[line.find("<... ") + 5:line.find(" resumed>")]

  # find unfinished system call
  unfinished_syscall_index = None
  for index in range(0, len(unfinished_syscall), 1):
    if unfinished_syscall[index].pid == pid and unfinished_syscall[index].command == command:
      unfinished_syscall_index = index
      break

  if unfinished_syscall_index == None:
    if DEBUG:
      log("Pending syscall not found.\n\n")
    return -1
  else:
    second_half = line[line.find("resumed>")+8:].strip()
    if second_half[0] != ')':
      second_half = " " + second_half

    pending = unfinished_syscall[unfinished_syscall_index]
    line = pending.firstHalf + second_half
    unfinished_syscall.pop(unfinished_syscall_index)

    return line


def numToListOfFlags(num):
  mode_flags = {
    777: 'S_IRWXA',
    700: 'S_IRWXU',
    400: 'S_IRUSR',
    200: 'S_IWUSR',
    100: 'S_IXUSR',
    70: 'S_IRWXG',
    40: 'S_IRGRP',
    20: 'S_IWGRP',
    10: 'S_IXGRP',
    7: 'S_IRWXO',
    4: 'S_IROTH',
    2: 'S_IWOTH',
    1: 'S_IXOTH'}
  
  list_of_flags = []
  if num == 777:
    list_of_flags.append(mode_flags[777])
  else:
    numerator = num
    denominator = 100
    for position in range(3):
      entity = int(numerator // denominator)
      
      if entity == 700 or entity == 70 or entity == 7:
        list_of_flags.append(mode_flags[entity])
      else:
        for flag in mode_flags:
          if flag > 7*denominator or flag < denominator:
            continue
          compare = int(str(flag).strip('0'))
          if entity & compare == compare:
            list_of_flags.append(mode_flags[flag])
      
      numerator %= denominator
      denominator /= 10
  return list_of_flags


'''
# For testing purposes...
def main():
    fh = open(FILE_NAME, "r")
    trace = getTraces(fh)
    log("\n")
    for action in trace:
        log("Action: ", action, "\n")

main()
'''
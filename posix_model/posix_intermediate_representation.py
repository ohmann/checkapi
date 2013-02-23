"""
<Program>
  posix_strace_parser.py

<Started>
  February 2013

<Author>
  Savvas Savvides

<Purpose>
  This file provides information on how to parse traces and translate 
  them to the intermediate representation.

  Firstly, a set of objects is provided with each object holding
  information on how to parse a specific 'type' of argument. Here 
  'type' could mean a conventional type like int or string but also
  includes things like lists or combinations of types, eg None or
  String.

  The second part of this program is dictionary that holds
  information that define what are the expected arguments and the
  expected return values of each system call. The final format of the
  intermediate representation is also defined in this dictionary.

"""
#############
# CONSTANTS #
#############

# This error shows that a system call did not have an expected value.
# This can happen for instance when a system call has an error in which
# case values of structures are not returned.
# Example (fstat on success and on error):
# 19243 fstat64(3, {st_mode=S_IFREG|0644, st_size=98710, ...}) = 0
# 19243 fstatfs(3, 0xbff476cc) = -1 EBADF (Bad file descriptor)
MISSING_ARGUMENT = -2


####################################################
# Classes that define the expected format and type #
# of arguments and return values of system calls.  #
####################################################
class Skip():
  """Indicates skip argument."""
  def __init__(self, output=False):
    self.output = output


class SkipRemaining():
  """Indicates skip all remaining arguments."""
  def __init__(self, output=False):
    self.output = output


class Int():
  """Parses int."""
  def __init__(self, output=False):
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
    except ValueError:
      raise Exception("Unexpected format when parsing type: " + type(val))
    return val


class Str():
  """Parses str or unicode."""
  def __init__(self, output=False):
    self.output = output
 
  def parse(self, val):
    if not (type(val) is str or type(val) is unicode):
      raise Exception("Unexpected format when parsing type: " + type(val))

    if val.endswith('\"...'):
      val = val[:val.rfind('...')]
    # strace always wraps strings in double quotes.
    if not val.startswith('\"') or not val.endswith('\"'):
      raise Exception("Unexpected format when parsing type: " + type(val))
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
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    return _stringToListOfFlags(val)


class Mode():
  """Parses mode_t. Translates number or list of flags."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    try:
      val = int(val)
    except ValueError:
      raise Exception("Unexpected format when parsing type: " + type(val))
    return _numToListOfFlags(val)


class IntOrListOfStr():
  """Parses int or list of strings."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    try:
      val = int(val)
    except ValueError:
      val = _stringToListOfFlags(val)
    return val


class IntOrQuestionOrListOfStr():
  """Parses int or question mark or list of strings
  
  int covers most cases
  queston mark appears in some rare cases eg in exit_group
  
  ListOfStr appears only in fcntl which returns a hex followed by a
  set of flags. Only the set of flags is passed here.
  """
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    try:
      val = int(val)
    except ValueError:
      if val == '?':
        return val
      return _stringToListOfFlags(val)
    return val


class NoneOrStr():
  """Parses a NoneType or a string."""
  def __init__(self, output=False):
    self.output = output
 
  def parse(self, val):
    if val is not None and not (type(val) is str or type(val) is unicode):
      raise Exception("Unexpected format when parsing type: " + type(val))
    return val


class SockFamily():
  """
  Parses sa_family of struct sockaddr.
  Example syscall that includes sa_family:
  19176 bind(3, {sa_family=AF_INET, sin_port=htons(25588), sin_addr=inet_addr("127.0.0.1")}, 16) = 0
  """
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    if val.find('sa_family=') == -1:
      raise Exception("Unexpected format when parsing type: " + type(val))
    # parse the family, skipping the 'sa_family' bit.
    val = val[val.find('sa_family=')+len('sa_family='):]
    return _stringToListOfFlags(val)


class SockIP():
  """
  Parses sin_addr of struct sockaddr.
  Example syscall that includes sin_addr:
  19176 bind(3, {sa_family=AF_INET, sin_port=htons(25588), sin_addr=inet_addr("127.0.0.1")}, 16) = 0
  """
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    # IP is given in the format 'inet_addr("A.B.C.D")'
    if val.find('inet_addr(\"') == -1 or val.find('\")') == -1:
      raise Exception("Unexpected format when parsing type: " + type(val))
    # parse the ip address skipping the parts that wrap it.
    val = val[val.find('inet_addr(\"')+len('inet_addr(\"'):val.rfind('\")')]
    return val


class SockPort():
  """
  Parses sin_port of struct sockaddr.
  Example syscall that includes sin_port:
  19176 bind(3, {sa_family=AF_INET, sin_port=htons(25588), sin_addr=inet_addr("127.0.0.1")}, 16) = 0
  """
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    # Port is given in the format 'htons(#####)'
    if val.find('htons(') == -1 or val.find(')') == -1:
      raise Exception("Unexpected format when parsing type: " + type(val))
    try:
      # parse the port skipping the parts that wrap it.
      val = int(val[val.find('htons(')+len('htons('):val.find(')')])
    except ValueError:
      raise Exception("Unexpected format when parsing type: " + type(val))
    return val


class StMode():
  """Parses st_mode of struct stat."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    if val.find('st_mode=') == -1:
      # if the syscall had an error the address of the struct is 
      # returned instead.
      if val.startswith('0x'):
        return MISSING_ARGUMENT
      raise Exception("Unexpected format when parsing type: " + type(val))
    # parse the mode skipping the preceding label.
    val = val[val.find('st_mode=')+len('st_mode='):]
    return _stringToListOfFlags(val)


class StSize():
  """Parses st_size of struct stat."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    if val.find('st_size=') == -1:
      raise Exception("Unexpected format when parsing type: " + type(val))
    try:
      # parse the size skipping the preceding label.
      val = int(val[val.find('st_size=')+len('st_size='):])
    except ValueError:
      raise Exception("Unexpected format when parsing type: " + type(val))
    return val


class FType():
  """Parses f_type of struct statfs."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    if val.find('f_type=') == -1:
      # if the syscall had an error the address of the struct is 
      # returned instead.
      if val.startswith('0x'):
        return MISSING_ARGUMENT
      raise Exception("Invalid type " + type(val))
    # parse the type skipping the preceding label.
    val = val[val.find('f_type=')+len('f_type='):]
    # val should be wrapped in double quotes.
    if not val.startswith('\"') or not val.endswith('\"'):
      raise Exception("Unexpected format when parsing type: " + type(val))
    # remove double quotes.
    val = val[1:-1]
    return val


class FBsize():
  """Parses f_bsize of struct statfs."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    if val.find('f_bsize=') == -1:
      raise Exception("Unexpected format when parsing type: " + type(val))
    try:
      # parse the bsize skipping the preceding label.
      val = int(val[val.find('f_bsize=')+len('f_bsize='):])
    except ValueError:
      raise Exception("Unexpected format when parsing type: " + type(val))
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
    'args': (Int(), FType(), FBsize(), SkipRemaining()),
    'return': (IntOrQuestionOrListOfStr(), NoneOrStr())
  },
  # int statfs(const char *path, struct statfs *buf);
  # 
  # Example strace output:
  # 19323 statfs("syscalls.txt", {f_type="EXT2_SUPER_MAGIC", f_bsize=4096, f_blocks=4553183, f_bfree=1458896, f_bavail=1227600, f_files=1158720, f_ffree=658713, f_fsid={-1853641883, -1823071587}, f_namelen=255, f_frsize=4096}) = 0
  "statfs": {
    'args': (Str(), FType(), FBsize(), SkipRemaining()),
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


#####################
# Helper Functions. #
#####################
def _stringToListOfFlags(flags_string):
  """
  Transforms a string to a list of flags.
  """
  flags_list = []
  temp_list = flags_string.split("|")
  for flag in temp_list:
    try:
      flag_int = int(flag.strip('0'))
    except ValueError:
      flags_list.append(flag)
    else:
      # number witin a list of flags. Example:
      # 19175 fstat64(3, {st_mode=S_IFREG|0755, st_size=1730024, ...}) = 0
      flags_list += _numToListOfFlags(flag_int)
  return flags_list


def _numToListOfFlags(num):
  """
  Transforms a number to a list of flags.
  """
  mode_flags = {
    777: 'S_IRWXA', 700: 'S_IRWXU', 400: 'S_IRUSR', 200: 'S_IWUSR',
    100: 'S_IXUSR', 70: 'S_IRWXG', 40: 'S_IRGRP', 20: 'S_IWGRP',
    10: 'S_IXGRP', 7: 'S_IRWXO', 4: 'S_IROTH', 2: 'S_IWOTH',
    1: 'S_IXOTH'}
  
  list_of_flags = []
  # check for all permissions.
  if num == 777:
    list_of_flags.append(mode_flags[777])
  else:
    # deal with each digit at a time (user then group then other)
    numerator = num
    denominator = 100
    for position in range(3):
      entity = int(numerator // denominator)
      
      # check if current entity has all permissions
      if entity == 7:
        list_of_flags.append(mode_flags[entity*denominator])
      else:
        # check entity for each flag.
        for flag in mode_flags:
          if flag > 7*denominator or flag < denominator:
            continue
          compare = int(str(flag).strip('0'))
          if entity & compare == compare:
            list_of_flags.append(mode_flags[flag])
      
      numerator %= denominator
      denominator /= 10
  return list_of_flags
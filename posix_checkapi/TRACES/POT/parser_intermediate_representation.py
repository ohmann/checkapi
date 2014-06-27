"""
<Program>
  parser_intermediate_representation.py

<Started>
  February 2013

<Author>
  Savvas Savvides

<Purpose>
  This file provides information on how to parse traces and translate 
  them to the intermediate representation.

  Firstly, a set of Classes is provided with each class holding
  information on how to parse a specific 'type' of argument. Here 
  'type' could mean a conventional type like int or string but also
  includes things like lists or combinations of types. Each of these
  classes has a parse function which takes as an argument the value
  of the expected type. This argument has the format used in the
  trace. The aim of this function is to strip this argument off
  unnecessary information and reformat it to the representation
  needede by the IR. If this function is called with no arguments or
  the given argument is not of the expected format, an Unknown object
  is returned.

  The second part of this program is dictionary that holds
  information that define what are the expected arguments and the
  expected return values of each system call. The final format of the
  intermediate representation is also defined in this dictionary.
"""

# This object is used to indicate that a system call did not return
# the expected value.
# This can happen for instance when a system call has an error,
# in which case values of structures are not returned.
# Example (fstat on success and on error):
# 19243 fstat64(3, {st_mode=S_IFREG|0644, st_size=98710, ...}) = 0
# 19243 fstatfs(3, 0xbff476cc) = -1 EBADF (Bad file descriptor)
#
# The equality operator is overriden and only returns true if the 
# other object is also of type Unknown
# Less than and Greater than operators are also overriden and
# immediately raise an exception if used, since no such operations
# are allowed with the Unknown object.
# 
# Finally the Unknown object includes two variables used to provide
# some information on why an item is of type Unknown. The first
# variable shows the expected type the item would normally have and
# the second variable shows the given value that caused the item to
# be of type Unknown instead. The repr operator is then overriden to
# provide a user friendly message.
class Unknown():
  def __init__(self, t=None, v=None):
    self.expected_type = t
    self.given_value = v
  # override equality
  def __eq__(self, other):
    return type(other) is type(self)
  # override inequality 
  def __ne__(self, other):
    return not self.__eq__(other)
  # override less than 
  def __lt__(self, other):
    raise Exception("Comparing object of type " + type(other) + 
                    " with Unknown object.")
  # greater than behaves exactly like less than.
  def __gt__(self, other):
    return self.__lt__(other)
  # override representation and string
  def __repr__(self):
    return "<Unknown, expected_type=" + repr(self.expected_type) + \
            ", given_value=" + repr(self.given_value) + ">"
  def __str__(self):
    return self.__repr__()



#####################################################
# Classes that define the expected format, the type #
# of arguments and return values of system calls.   #
#####################################################
class SkipRemaining():
  """
  Indicates skip all remaining arguments.
  Useful for system calls that are not fully supported.
  """
  def __init__(self, output=False):
    self.output = output
  def parse(self):
    return Unknown('SkipRemaining')


class Int():
  """Parses int."""
  def __init__(self, label_left=None, label_right=None, output=False):
    self.label_left = label_left
    self.label_right = label_right
    self.output = output

  def parse(self, val=None):
    if val == None or val == "":
      return Unknown('Int', val)
    # if the value starts with 0x it was not dereferenced.
    if val.startswith('0x'):
      return Unknown('Int', val)
    
    # remove lables
    val = _remove_labels(val, self.label_left, self.label_right)
    if val == "":
      return Unknown('Int', val)

    # dereferenced numbers are wrapped in []
    if val.startswith('[') and val.endswith(']'):
      val = val[1:-1]
      
    try:
      val = int(val)
    except ValueError:
      raise Exception("Unexpected format when parsing Int: " + val)
    return val


class Str():
  """Parses str or unicode."""
  def __init__(self, label_left=None, label_right=None, output=False):
    self.label_left = label_left
    self.label_right = label_right
    self.output = output
 
  def parse(self, val=None):
    if val == None:
      return Unknown('Str', val)
    # if the value starts with 0x it was not dereferenced.
    if self.label_left != None and val.startswith('0x'):
      return Unknown('Str', val)
    # remove lables
    val = _remove_labels(val, self.label_left, self.label_right)

    if not (type(val) is str or type(val) is unicode):
      raise Exception("Unexpected format when parsing value: " + val)
    if val.endswith('\"...'):
      val = val[:val.rfind('...')]
    if val.startswith('\"') and val.endswith('\"'):
      # remove double quotes.
      val = val[1:-1]
    elif val.startswith('\"') or val.endswith('\"'):
      raise Exception("String with only one quote.")

    # replace special characters.
    val = val.replace("\\n", "\n")
    val = val.replace("\\r", "\r")
    val = val.replace("\\t", "\t")
    val = val.replace("\\0", "\0")
    return val

class SockPath():
  """Parses path from a sockaddr."""
  def __init__(self, label_left=None, label_right=None, output=False):
    self.label_left = label_left
    self.label_right = label_right
    self.output = output
 
  def parse(self, val=None):
    if val == None:
      return Unknown('SockPath', val)
    # if the value starts with 0x it was not dereferenced.
    if self.label_left != None and val.startswith('0x'):
      return Unknown('SockPath', val)
    # remove lables
    val = _remove_labels(val, self.label_left, self.label_right)

    if val == "NULL":
      return val

    if val.startswith("path="):
      return val[5:]

    raise Exception("Unexpected format of SockPath")

class Mode():
  """Parses mode_t. Translates number to list of flags."""
  def __init__(self, output=False):
    self.output = output
  
  def parse(self, val=None):
    if val == None or val == "":
      return Unknown('Mode', val)
    try:
      val = int(val)
    except ValueError:
      raise Exception("Unexpected format when parsing Mode: " + val)
    return _modeToListOfFlags(val)


class ZeroOrListOfFlags():
  """Parses 0 or list of strings."""
  def __init__(self, label_left=None, label_right=None, output=False):
    self.label_left = label_left
    self.label_right = label_right
    self.output = output

  def parse(self, val=None):
    if val == None or val == "":
      return Unknown('ZeroOrListOfFlags', val)
    # if the value starts with 0x it was not dereferenced.
    if self.label_left != None and val.startswith('0x'):
      return Unknown('ZeroOrListOfFlags', val)
    # remove lables
    val = _remove_labels(val, self.label_left, self.label_right)
    if val == "":
      return Unknown('ZeroOrListOfFlags', val)
    
    if val.isdigit():
      val = int(val)
      if val == 0:
        return val
      else:
        return Unknown('ZeroOrListOfFlags', val)
    # if not a number then it must be a list of flags.
    return _stringToListOfFlags(val)


class IntOrQuestionOrListOfFlags():
  """Parses int or question mark or list of strings
  
  int covers most cases
  question mark appears in some rare cases eg in exit_group
  
  List of flags appears only in fcntl which returns a hex followed by
  a set of flags. Only the set of flags is passed here.
  """
  def __init__(self, output=False):
    self.output = output

  def parse(self, val=None):
    if val == None or val == "":
      return Unknown('IntOrQuestionOrListOfFlags', val)
    try:
      val = int(val)
    except ValueError:
      if val == '?':
        val = -1
      else:
        val = _stringToListOfFlags(val)
    return val


class NoneOrStr():
  """Parses a NoneType or a string."""
  def __init__(self, output=False):
    self.output = output
 
  def parse(self, val=""):
    if val == "":
      return Unknown('NoneOrStr', val)
    if (val is not None and not 
       (type(val) is str or type(val) is unicode)):
      raise Exception("Unexpected format when parsing value: " + val)
    return val


class StSizeOrRdev():
  """Parses st_size or st_rdev of struct stat."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val=None):
    if val == None or val == "" or val.startswith('0x'):
      return Unknown('StSizeOrRdev', val)
    # if the label is not found in the value parsing, raise an
    # exception.
    if val.find('st_size=') != -1:
      # st size should have a number
      try:
        # parse the value skipping the preceding label.
        val = int(val[val.find('st_size=')+8:])
      except ValueError:
        raise Exception("Unexpected format when parsing StSizeOrRdev")
    elif val.find('st_rdev=') != -1:
      # st_rdef parses a string
      val[val.find('st_rdev=')+8:]
    else:
      raise Exception("Unexpected format when parsing value: " + val)
 
    return val


class StDev():
  """Parses st_dev of struct stat."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val=None):
    if val == None or val == "" or val.startswith('0x'):
      return Unknown('StDev', val)
    # if the label is not found in the value parsing, raise an
    # exception.
    if val.find('st_dev=') == -1:
      raise Exception("Unexpected format when parsing value: " + val)
    return val[val.find('st_dev=')+7:]


class FFsid():
  """Parses f_fsid of statfs."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val=None):
    if val == None or val == "" or val.startswith('0x'):
      return Unknown('FFsid', val)
    if val.startswith("f_fsid="):
      val = val[val.find("f_fsid=")+7:]
    else:
      raise Exception("Unexpected format when parsing FFsid", val)
    return val


class IoctlRequest():
  """Parses request part of ioctl."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val=None):
    if val == None or val == "":
      return Unknown('IoctlRequest', val)
    requests = val.split()
    # remove all occurences of or
    requests = [item for item in requests if item != "or"]
    return requests


class FdSet():
  """Parses fd_set of select."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val=None):
    if val == None or val == "":
      return Unknown('FdSet', val)
    if val == 'NULL':
      val = []
    else:
      # get a list of the fds and convert them to integers
      val = val.replace("\'", "")
      val = val.replace("[", "")
      val = val.replace("]", "")
      val = map(int, val.split())
    return val


class TimeVal():
  """Parses timeval of select."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val=None):
    if val == None or val == "":
      return Unknown('TimeVal', val)
    if val.find("{") == -1 or val.find("}") == -1:
      raise Exception("Unexpected format when parsing value: " + val)
    else:
      val = val.replace("{", "")
      val = val.replace("}", "")
      val = val.replace(",", "")
      val = map(int, val.split())
    return val


"""
Information about individual system calls.
The declaration of each syscall is provided in comments followed by
one or more examples of strace output for that syscall.
The strace general output format is as follows:
pid syscall_name(args) = return

This information is used for parsing and translating traces to the
intermediate representation.
The general format of the intermediate representation is:
('syscallName_syscall', (args1, arg2, ...), (return1, return2, ...))
where the order of args and return values is the same as the order
they appear in the trace output.

Each syscall has a set of arguments and return values associated with
it. Each argument or return value is represented by a class, which
defines its expected format when parsing it, and its expected type
when translating it to the intermediate representation. These classes
can optionally take an argument "output=True" which indicates that the
current argument is used to return a value rather than to pass a
value, and hence the argument should be moved in the return part of
the intermediate representation.
"""

""" 
TODO:

Add support for:
  - writev
  - sendfile
"""
HANDLED_SYSCALLS_INFO = {
  # int accept(int sockfd, struct sockaddr *addr, socklen_t *addrlen);
  # 
  # Example strace output:
  # 19176 accept(3, {sa_family=AF_INET, sin_port=htons(42572),
  #              sin_addr=inet_addr("127.0.0.1")}, [16]) = 4
  "accept": {
    'args': (Int(), 
             ZeroOrListOfFlags(label_left="sa_family=", output=True), 
             Int(label_left="sin_port=htons(", label_right=")", 
                 output=True),
             Str(label_left="sin_addr=inet_addr(", label_right=")", 
                 output=True), 
             Int(output=True)),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },

  # int access(const char *pathname, int mode);
  # 
  # Example strace output:
  # 19178 access("syscalls.txt", F_OK) = 0
  # 19178 access("syscalls.txt", R_OK|W_OK) = 0
  # 19178 access("syscalls.txt", X_OK) = -1 EACCES (Permission denied)
  "access": {
    'args': (Str(), ZeroOrListOfFlags()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },

  # int bind(int sockfd, const struct sockaddr *addr, 
  #          socklen_t addrlen);
  # 
  # Example strace output:
  # 19176 bind(3, {sa_family=AF_INET, sin_port=htons(25588), 
  #                sin_addr=inet_addr("127.0.0.1")}, 16) = 0
  # 19184 bind(3, {sa_family=AF_INET, sin_port=htons(25588), 
  #                sin_addr=inet_addr("127.0.0.1")}, 16) = -1 
  #                         EADDRINUSE (Address already in use)
  "bind": {
    'args': (Int(), ZeroOrListOfFlags(label_left="sa_family="), 
            Int(label_left="sin_port=htons(", label_right=")"), 
            Str(label_left="sin_addr=inet_addr(", label_right=")"), 
            Int()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  
  # int chdir(const char *path);
  # 
  # Example strace output:
  # 19217 chdir(".") = 0
  "chdir": {
    'args': (Str(),),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },

  # int clone(int (*fn)(void *), void *child_stack, int flags, 
  #           void *arg, ... /* pid_t *ptid, struct user_desc *tls, 
  #           pid_t *ctid */ );
  # 
  # Example strace output:
  # 7122 clone(child_stack=0xb7507464, 
  #            flags=CLONE_VM|CLONE_FS|CLONE_FILES|CLONE_SIGHAND|
  #                  CLONE_THREAD|CLONE_SYSVSEM|CLONE_SETTLS|
  #                  CLONE_PARENT_SETTID|CLONE_CHILD_CLEARTID, 
  #            parent_tidptr=0xb7507ba8, {entry_number:6, 
  #            base_addr:0xb7507b40, limit:1048575, seg_32bit:1, 
  #            contents:0, read_exec_only:0, limit_in_pages:1, 
  #            seg_not_present:0, useable:1}, 
  #            child_tidptr=0xb7507ba8) = 7123
  # 
  "clone": {
    'args': (Str(label_left="child_stack="), 
             ZeroOrListOfFlags(label_left="flags="),
             SkipRemaining()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },

  # int socket(int domain, int type, int protocol);
  # 
  # Example strace output:
  # 19176 socket(PF_INET, SOCK_STREAM, IPPROTO_IP) = 3
  # 19294 socket(PF_INET, SOCK_DGRAM, IPPROTO_UDP) = 3
  "socket": {
    'args': (ZeroOrListOfFlags(), ZeroOrListOfFlags(), 
             ZeroOrListOfFlags()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  
  # int connect(int sockfd, const struct sockaddr *addr, 
  #             socklen_t addrlen);
  # 
  # Example strace output:
  # 19175 connect(5, {sa_family=AF_INET, sin_port=htons(25588), 
  #                   sin_addr=inet_addr("127.0.0.1")}, 16) = 0
  # 19262 connect(5, {sa_family=AF_INET, sin_port=htons(25588), 
  #                   sin_addr=inet_addr("127.0.0.1")}, 16) = -1 
  #                             ECONNREFUSED (Connection refused)
  "connect": {
    'args': (Int(), ZeroOrListOfFlags(label_left="sa_family="), 
             Int(label_left="sin_port=htons(", label_right=")"), 
             Str(label_left="sin_addr=inet_addr(", label_right=")"), 
             Int()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # ssize_t sendto(int sockfd, const void *buf, size_t len, 
  #                int flags, const struct sockaddr *dest_addr, 
  #                socklen_t addrlen);
  # 
  # Example strace output:
  # 19309 sendto(3, "Message for sendto.\0", 20, 0, 
  #              {sa_family=AF_INET, sin_port=htons(25588), 
  #              sin_addr=inet_addr("127.0.0.1")}, 16) = 20
  "sendto": {
    'args': (Int(), Str(), Int(), ZeroOrListOfFlags(), 
             ZeroOrListOfFlags(label_left="sa_family="), 
             Int(label_left="sin_port=htons(", label_right=")"), 
             Str(label_left="sin_addr=inet_addr(", label_right=")"), 
             Int()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # ssize_t send(int sockfd, const void *buf, size_t len, int flags);
  # 
  # Example strace output:
  # 19285 send(4, "Message to be received.\0", 24, 0) = 24
  # 19304 send(5, "\0\0c\364", 4, 0)        = -1 EPIPE (Broken pipe)
  "send": {
    'args': (Int(), Str(), Int(), ZeroOrListOfFlags()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # ssize_t recvfrom(int sockfd, void *buf, size_t len, int flags,
  #                  struct sockaddr *src_addr, socklen_t *addrlen);
  # 
  # Example strace output:
  # 19294 recvfrom(3, "Message for sendto.\0", 512, 0, 
  #                {sa_family=AF_INET, sin_port=htons(40299), 
  #                sin_addr=inet_addr("127.0.0.1")}, [16]) = 20
  "recvfrom": {
    'args': (Int(), Str(output=True), Int(), ZeroOrListOfFlags(), 
             ZeroOrListOfFlags(label_left="sa_family=", output=True), 
             Int(label_left="sin_port=htons(", label_right=")", 
                 output=True),
             Str(label_left="sin_addr=inet_addr(", label_right=")", 
                 output=True), 
             Int(output=True)),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # ssize_t recv(int sockfd, void *buf, size_t len, int flags);
  # 
  # Example strace output:
  # 19284 recv(5, "Message to be received.\0", 24, 0) = 24
  "recv": {
    'args': (Int(), Str(output=True), Int(), ZeroOrListOfFlags()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int getsockname(int sockfd, struct sockaddr *addr, 
  #                 socklen_t *addrlen);
  # 
  # Example strace output:
  # 19255 getsockname(3, {sa_family=AF_INET, sin_port=htons(0), 
  #                   sin_addr=inet_addr("0.0.0.0")}, [16]) = 0
  "getsockname": {
    'args': (Int(), 
             ZeroOrListOfFlags(label_left="sa_family=", output=True), 
             Int(label_left="sin_port=htons(", label_right=")", 
                 output=True),
             Str(label_left="sin_addr=inet_addr(", label_right=")", 
                 output=True), Int(output=True)),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int   getpeername(int sockfd, struct sockaddr *addr, 
  #                   socklen_t *addrlen);
  # 
  # Example strace output:
  # 19252 getpeername(5, {sa_family=AF_INET, sin_port=htons(25588), 
  #                   sin_addr=inet_addr("127.0.0.1")}, [16]) = 0
  "getpeername": {
    'args': (Int(), 
             ZeroOrListOfFlags(label_left="sa_family=", output=True), 
             Int(label_left="sin_port=htons(", label_right=")", 
                 output=True),
             Str(label_left="sin_addr=inet_addr(", label_right=")", 
                 output=True), Int(output=True)),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int listen(int sockfd, int backlog);
  # 
  # Example strace output:
  # 19176 listen(3, 5) = 0
  "listen": {
    'args': (Int(), Int()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },

  # int getsockopt(int sockfd, int level, int optname, void *optval, 
  #                socklen_t *optlen);
  # 
  # Example strace output:
  # 19258 getsockopt(3, SOL_SOCKET, SO_TYPE, [1], [4]) = 0
  # 19258 getsockopt(3, SOL_SOCKET, SO_OOBINLINE, [0], [4]) = 0
  "getsockopt": {
    'args': (Int(), ZeroOrListOfFlags(), ZeroOrListOfFlags(), 
             Int(output=True), Int(output=True)),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int setsockopt(int sockfd, int level, int optname, void *optval, 
  #                socklen_t optlen);
  # 
  # Example strace output:
  # 19313 setsockopt(3, SOL_SOCKET, SO_REUSEADDR, [1], 4) = 0
  "setsockopt": {
    'args': (Int(), ZeroOrListOfFlags(), ZeroOrListOfFlags(), Int(), 
             Int()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int shutdown(int sockfd, int how);
  # 
  # Example strace output:
  # 19316 shutdown(5, 0 /* receive */) = 0
  # 19316 shutdown(5, 2 /* send and receive */) = 0
  "shutdown": {
    'args': (Int(), ZeroOrListOfFlags()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int close(int fd);
  # 
  # Example strace output:
  # 19319 close(3) = 0
  "close": {
    'args': (Int(),),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int fstatfs(int fd, struct statfs *buf);
  # 
  # Example strace output:
  # 19243 fstatfs(3, {f_type="EXT2_SUPER_MAGIC", f_bsize=4096, 
  #    f_blocks=4553183, f_bfree=1457902, f_bavail=1226606, 
  #    f_files=1158720, f_ffree=658673, f_fsid={-1853641883, 
  #    -1823071587}, f_namelen=255, f_frsize=4096}) = 0
  "fstatfs": {
    'args': (Int(), 
             Str(label_left="f_type=", output=True), 
             Int(label_left="f_bsize=", output=True), 
             Int(label_left="f_blocks=", output=True), 
             Int(label_left="f_bfree=", output=True), 
             Int(label_left="f_bavail=", output=True), 
             Int(label_left="f_files=", output=True), 
             Int(label_left="f_ffree=", output=True), 
             FFsid(output=True), 
             Int(label_left="f_namelen=", output=True), 
             Int(label_left="f_frsize=", label_right="}", output=True)),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int statfs(const char *path, struct statfs *buf);
  # 
  # Example strace output:
  # 19323 statfs("syscalls.txt", {f_type="EXT2_SUPER_MAGIC", 
  #     f_bsize=4096, f_blocks=4553183, f_bfree=1458896, 
  #     f_bavail=1227600, f_files=1158720, f_ffree=658713, 
  #     f_fsid={-1853641883, -1823071587}, f_namelen=255, 
  #     f_frsize=4096}) = 0
  "statfs": {
    'args': (Str(), Str(label_left="f_type=", output=True), 
             Int(label_left="f_bsize=", output=True), 
             Int(label_left="f_blocks=", output=True), 
             Int(label_left="f_bfree=", output=True), 
             Int(label_left="f_bavail=", output=True), 
             Int(label_left="f_files=", output=True), 
             Int(label_left="f_ffree=", output=True), 
             FFsid(output=True), 
             Int(label_left="f_namelen=", output=True), 
             Int(label_left="f_frsize=", label_right="}", output=True)),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  
  
  # int mkdir(const char *pathname, mode_t mode);
  # 
  # Example strace output:
  # 19269 mkdir("syscalls_dir", 0775) = -1 EEXIST (File exists)
  "mkdir": {
    'args': (Str(), Mode()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int rmdir(const char *pathname);
  # 
  # Example strace output:
  # 19302 rmdir("syscalls_dir") = 0
  "rmdir": {
    'args': (Str(),),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int link(const char *oldpath, const char *newpath);
  # 
  # Example strace output:
  # 19260 link("syscalls.txt", "syscalls.link") = -1 
  #            EEXIST (File exists)
  # 19260 link("hopefully_no_such_filename_exists.txt", 
  #         "syscalls2.link") = -1 ENOENT (No such file or directory)
  "link": {
    'args': (Str(), Str()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int symlink(const char *oldpath, const char *newpath);
  # 
  # Example strace output:
  # 19267 symlink("syscalls.txt", "syscalls.symlink") = 0
  "symlink": {
    'args': (Str(), Str()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int unlink(const char *pathname);
  # 
  # Example strace output:
  # 19327 unlink("syscalls.txt") = 0
  # 19327 unlink("syscalls.symlink")        = 0
  # 19327 unlink("hopefully_no_such_filename_exists.txt") = -1 ENOENT 
  #                                    (No such file or directory)
  "unlink": {
    'args': (Str(),),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int stat(const char *path, struct stat *buf);
  # 
  # Example strace output:
  # 10538 stat64("syscalls.txt", {st_dev=makedev(8, 6), st_ino=697814,
  #    st_mode=S_IFREG|0664, st_nlink=1, st_uid=1000, st_gid=1000, 
  #    st_blksize=4096, st_blocks=0, st_size=0, 
  #    st_atime=2013/03/06-00:17:54, st_mtime=2013/03/06-00:17:54, 
  #    st_ctime=2013/03/06-00:17:54}) = 0
  # 19321 stat64("hopefully_no_such_filename_exists.txt", 
  #              0xbf8c7d50) = -1 ENOENT (No such file or directory)
  #
  # Example truss output:
  # 2303: stat64("/savvas/syscalls", 0x08047130)    = 0
  # 2303:     d=0x00780000 i=299777 m=0100755 l=1  u=0     g=0     sz=59236
  # 2303:   at = Apr 25 22:54:48 EDT 2013  [ 1366944888.736170000 ]
  # 2303:   mt = Apr 25 21:43:45 EDT 2013  [ 1366940625.857272000 ]
  # 2303:   ct = Apr 25 21:43:45 EDT 2013  [ 1366940625.857272000 ]
  # 2303:     bsz=8192  blks=116   fs=ufs
  "stat": {
    'args': (Str(), StDev(output=True), 
             Int(label_left="st_ino=", output=True), 
             ZeroOrListOfFlags(label_left="st_mode=", output=True), 
             Int(label_left="st_nlink=", output=True), 
             Int(label_left="st_uid=", output=True), 
             Int(label_left="st_gid=", output=True), 
             Int(label_left="st_blksize=", output=True), 
             Int(label_left="st_blocks=", output=True), 
             StSizeOrRdev(output=True), 
             Str(label_left="st_atime=", output=True), 
             Str(label_left="st_mtime=", output=True), 
             Str(label_left="st_ctime=", label_right="}", output=True)
             ),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int fstat(int fd, struct stat *buf);
  # 
  # Example strace output:
  # 10605 fstat64(3, {st_dev=makedev(8, 6), st_ino=697814, 
  #                   st_mode=S_IFREG|0664, st_nlink=1, st_uid=1000, 
  #                   st_gid=1000, st_blksize=4096, st_blocks=0, 
  #                   st_size=0, st_atime=2013/03/06-00:17:54, 
  #                   st_mtime=2013/03/06-00:17:54, 
  #                   st_ctime=2013/03/06-00:17:54}) = 0
  # 32566 fstat64(0, {st_dev=makedev(0, 11), st_ino=8, 
  #               st_mode=S_IFCHR|0620, st_nlink=1, st_uid=1000, 
  #               st_gid=5, st_blksize=1024, st_blocks=0, 
  #               st_rdev=makedev(136, 5), 
  #               st_atime=2013/03/05-11:15:44, 
  #               st_mtime=2013/03/05-11:15:44, 
  #               st_ctime=2013/03/05-10:44:02}) = 0
  # 10605 fstat64(3, 0xbfb99fe0) = -1 EBADF (Bad file descriptor)
  "fstat": {
    'args': (Int(), StDev(output=True), 
             Int(label_left="st_ino=", output=True), 
             ZeroOrListOfFlags(label_left="st_mode=", output=True), 
             Int(label_left="st_nlink=", output=True), 
             Int(label_left="st_uid=", output=True), 
             Int(label_left="st_gid=", output=True), 
             Int(label_left="st_blksize=", output=True), 
             Int(label_left="st_blocks=", output=True), 
             StSizeOrRdev(output=True), 
             Str(label_left="st_atime=", output=True), 
             Str(label_left="st_mtime=", output=True), 
             Str(label_left="st_ctime=", label_right="}", output=True)),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int open(const char *pathname, int flags);
  # int open(const char *pathname, int flags, mode_t mode);
  # 
  # Example strace output:
  # 19224 open("syscalls.txt", O_RDONLY|O_CREAT, 0664) = 3
  # 19224 open("syscalls2.txt", O_RDWR|O_CREAT|O_APPEND, 0664) = 3
  "open": {
    'args': (Str(), ZeroOrListOfFlags(), Mode()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int creat(const char *pathname, mode_t mode);
  # 
  # Example strace output:
  # 19229 creat("syscalls.txt", 0666)       = 3
  # 19229 creat("syscalls2.txt", 0600)      = 4
  "creat": {
    'args': (Str(), Mode()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # off_t lseek(int fd, off_t offset, int whence);
  # 
  # Example strace output:
  # 19265 lseek(3, 1, SEEK_SET) = 1
  # 19265 lseek(3, 5, SEEK_CUR) = 16
  "lseek": {
    'args': (Int(), Int(), ZeroOrListOfFlags()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # ssize_t read(int fd, void *buf, size_t count);
  # 
  # Example strace output:
  # 19282 read(3, "abcdefghijklmnopqrst", 20) = 20
  "read": {
    'args': (Int(), Str(output=True), Int()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # ssize_t write(int fd, const void *buf, size_t count);
  # 
  # Example strace output:
  # 19265 write(3, "abcdefghijklmnopqrstuvwxyz", 26) = 26
  "write": {
    'args': (Int(), Str(), Int()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int dup(int oldfd);
  # 
  # Example strace output:
  # 19231 dup(3) = 4
  # 19231 dup(3) = -1 EBADF (Bad file descriptor)
  "dup": {
    'args': (Int(),),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int dup2(int oldfd, int newfd);
  # 
  # Example strace output:
  # 19233 dup2(3, 4) = 4
  # 19233 dup2(3, 3) = 3
  # 19233 dup2(3, -1) = -1 EBADF (Bad file descriptor)
  "dup2": {
    'args': (Int(), Int()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int dup3(int oldfd, int newfd, int flags);
  # 
  # Example strace output:
  # 19235 dup3(3, 4, O_CLOEXEC) = 4
  "dup3": {
    'args': (Int(), Int(), ZeroOrListOfFlags()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int getdents(unsigned int fd, struct linux_dirent *dirp, 
  #              unsigned int count);
  # 
  # Example strace output:
  # 10917 getdents(3, {{d_ino=709301, d_off=2124195000, d_reclen=28, 
  #                d_name="sendto.strace"} {d_ino=659266, 
  #                d_off=2147483647, d_reclen=32, 
  #                d_name="syscalls_functions.h"}}, 1024) = 60
  # 10917 getdents(3, {}, 1024) = 0
  "getdents": {
    'args': (Int(), Int()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int fcntl(int fd, int cmd, ... /* arg */ );
  # 
  # TODO: add support for third parameter of fcntl
  #
  # Example strace output:
  # 19239 fcntl64(3, F_GETFL) = 0 (flags O_RDONLY)
  # 19239 fcntl64(4, F_GETFL) = 0x402 (flags O_RDWR|O_APPEND)
  "fcntl": {
    'args': (Int(), ZeroOrListOfFlags()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },

  """
  TODO: 
  Deal with this case first:
  14041 recvmsg(8,  <unfinished ...>
    14039 getpid({msg_name(0)=NULL, msg_iov(1)=[{"l\2\1\1\f\0\0\0\1\0\0\0=\0\0\0", 16}], 
      msg_controllen=0, msg_flags=MSG_CMSG_CLOEXEC}, MSG_CMSG_CLOEXEC) = 16
  
  # ssize_t recvmsg(int sockfd, struct msghdr *msg, int flags);
  # 
  # Example strace output:
  # recvmsg(4, {msg_name(12)={sa_family=AF_NETLINK, pid=0, 
  #         groups=00000000}, msg_iov(1)=[{"\24\0\0gmai", 4096}], 
  #         msg_controllen=0, msg_flags=0}, 0) = 20
  "recvmsg": {
    'args': (Int(), 
             ZeroOrListOfFlags(label_left="sa_family=", output=True), 
             Int(label_left="sin_port=htons(", label_right=")", 
                 output=True),
             Str(label_left="sin_addr=inet_addr(", label_right=")", 
                 output=True), 
             Str(label_left="=[{", output=True), 
             Int(label_right="}", output=True), 
             Int(label_left="msg_controllen=", output=True),
             ZeroOrListOfFlags(label_left="msg_flags=", 
                              label_right="}", output=True), 
             ZeroOrListOfFlags()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  """

  """
  TODO: 
  Deal with this case first:
    14040 sendmsg(8, {msg_name(0)=NULL, msg_iov(1)=[{"\0", 1}], 
      msg_controllen=24, {cmsg_len=24, cmsg_level=SOL_SOCKET, 
      cmsg_type=SCM_CREDENTIALS{pid=14037, uid=1000, gid=1000}}, 
      msg_flags=0}, MSG_NOSIGNAL)           = 1

  # ssize_t sendmsg(int sockfd, const struct msghdr *msg, int flags);
  # 
  # Example strace output:
  # 19307 sendmsg(3, {msg_name(16)={sa_family=AF_INET, 
  #               sin_port=htons(25588), 
  #               sin_addr=inet_addr("127.0.0.1")}, 
  #               msg_iov(1)=[{"Message for sendmsg.\0", 21}], 
  #               msg_controllen=0, msg_flags=0}, 0) = 21
  "sendmsg": {
    'args': (Int(), 
             ZeroOrListOfFlags(label_left="sa_family="),
             Int(label_left="sin_port=htons(", label_right=")"),
             Str(label_left="sin_addr=inet_addr(", label_right=")"),
             Str(label_left="=[{"),
             Int(label_right="}"),
             Int(label_left="msg_controllen="),
             ZeroOrListOfFlags(label_left="msg_flags=", 
                               label_right="}"),
             ZeroOrListOfFlags()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  """
  
  # int ioctl(int d, int request, ...);
  # 
  # ioctl(0, SNDCTL_TMR_TIMEBASE or TCGETS, {c_iflags=0x6d02, 
  #       c_oflags=0x5, c_cflags=0x4bf, c_lflags=0x8a3b, c_line=0, 
  #       c_cc="\x03\x1c\x7f\x15\x017\x16\xff\x00\x00"}) = 0
  # ioctl(3, SNDCTL_TMR_TIMEBASE or TCGETS, 0xbfda9e08) 
  #                    = -1 ENOTTY (Inappropriate ioctl for device)
  # 
  "ioctl": {
    'args': (Int(), IoctlRequest(), SkipRemaining()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int select(int nfds, fd_set *readfds, fd_set *writefds,
  #                fd_set *exceptfds, struct timeval *timeout);
  # 
  # select(0, NULL, NULL, NULL, {1, 0})     = 0 (Timeout)
  # select(0, NULL, NULL, NULL, {1, 0})     = 0 (Timeout)
  "select": {
    'args': (Int(), FdSet(), FdSet(), FdSet(), TimeVal()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  }
}
"""
TODO:
  deal with the second example.

# int poll(struct pollfd *fds, nfds_t nfds, int timeout);
#
# poll([{fd=3, events=POLLOUT}], 1, 5000) = 1 ([{fd=3, 
#           revents=POLLOUT}])
# 
# 14041 poll([{fd=7, events=POLLIN}, {fd=8, events=POLLIN}, 
#            {fd=10, events=POLLIN}], 3, -1) = 1 ([{fd=7, revents=POLLIN}])
"poll": {
  'args': (Int(label_left="[{fd="), Str(label_left="events=", label_right="}]"), Int(), Int()),
  'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
}
"""


#####################
# Helper Functions. #
#####################
def _remove_labels(val, label_left, label_right):
  # remove the left label from the value
  if label_left != None:
    if val.find(label_left) == -1:
      raise Exception("Unexpected format when removing " + 
                      "left label", label_left, val)
    val = val[val.find(label_left)+len(label_left):]
  # remove the right label from the value
  if label_right != None:
    if val.find(label_right) == -1:
      raise Exception("Unexpected format when removing " + 
                      "right label", label_right, val)
    val = val[:val.rfind(label_right)]
  return val


def _stringToListOfFlags(flags_string):
  """
  Transforms a string to a list of flags.
  """
  flags_list = []
  
  # A a list of flags can also contain a mode in its numeric value.
  # Example:
  # 19243 fstat64(3, {st_mode=S_IFREG|0644, st_size=98710, ...}) = 0
  # go through all flags and translate numeric mode to flads.
  for flag in flags_string.split("|"):
    try:
      flag_int = int(flag.strip('0'))
      # numeric mode within a list of flags.
      # Example: S_IFREG|0755
      # translate to flags.
      flags_list += _modeToListOfFlags(flag_int)
    except ValueError:
      flags_list.append(flag)
  return flags_list


def _modeToListOfFlags(mode):
  """
  Transforms a number representing a mode to a list of flags.
  """
  mode_flags = {
    777: 'S_IRWXA', 700: 'S_IRWXU', 400: 'S_IRUSR', 200: 'S_IWUSR',
    100: 'S_IXUSR', 70: 'S_IRWXG', 40: 'S_IRGRP', 20: 'S_IWGRP',
    10: 'S_IXGRP', 7: 'S_IRWXO', 4: 'S_IROTH', 2: 'S_IWOTH',
    1: 'S_IXOTH'}

  list_of_flags = []
  # check for all permissions.
  if mode == 777:
    list_of_flags.append(mode_flags[777])
  else:
    # deal with each entity (digit) at a time (user then group
    # then other)
    mode_string = str(mode)
    # used to translate eg 7 to 700 for user.
    entity_position = 10**(len(mode_string)-1)
    for mode_character in str(mode):
      try:
        entity = int(mode_character)
      except ValueError:
        raise Exception("Unexpected mode format: " + str(mode))
      
      # is the mode in the correct format?
      if entity < 0 or entity > 7:
        raise Exception("Unexpected mode format: " + str(mode))
      
      # check if current entity has all permissions
      if entity == 7:
        list_of_flags.append(mode_flags[entity*entity_position])
      else:
        # check entity for each flag.
        for flag in mode_flags:
          if flag > 7*entity_position or flag < entity_position:
            continue
          compare = int(str(flag).strip('0'))
          if entity & compare == compare:
            list_of_flags.append(mode_flags[flag])
      
      entity_position /= 10
  return list_of_flags


#if __name__ == "__main__":
  #print "Supported Syscalls"
  #print "------------------"
  #count = 1
  #for syscall in sorted(HANDLED_SYSCALLS_INFO.keys()):
    #print str(count) + ": " + syscall
    #count += 1

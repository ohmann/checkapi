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

# This object is used to indicate that a system call did not return
# the expected value.
# This can happen for instance when a system call has an error,
# in which case values of structures are not returned.
# Example (fstat on success and on error):
# 19243 fstat64(3, {st_mode=S_IFREG|0644, st_size=98710, ...}) = 0
# 19243 fstatfs(3, 0xbff476cc) = -1 EBADF (Bad file descriptor)
class Unknown():
  # override equality
  def __eq__(self, other):
    return type(other) is type(self)
  # override inequality 
  def __ne__(self, other):
    return not self.__eq__(other)


####################################################
# Classes that define the expected format and type #
# of arguments and return values of system calls.  #
####################################################
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
      raise Exception("Unexpected format when parsing value: " + val)
    return val


class Str():
  """Parses str or unicode."""
  def __init__(self, output=False):
    self.output = output
 
  def parse(self, val):
    if not (type(val) is str or type(val) is unicode):
      raise Exception("Unexpected format when parsing value: " + val)

    if val.endswith('\"...'):
      val = val[:val.rfind('...')]
    # strace always wraps strings in double quotes.
    if not val.startswith('\"') or not val.endswith('\"'):
      raise Exception("Unexpected format when parsing value: " + val)
    # remove double quotes.
    val = val[1:-1]
    # replace special characters.
    val = val.replace("\\n", "\n")
    val = val.replace("\\r", "\r")
    val = val.replace("\\t", "\t")
    val = val.replace("\\0", "\0")
    return val


class Mode():
  """Parses mode_t. Translates number to list of flags."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    try:
      val = int(val)
    except ValueError:
      raise Exception("Unexpected format when parsing value: " + val)
    return _modeToListOfFlags(val)


class ZeroOrListOfFlags():
  """Parses 0 or list of strings."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    try:
      # is val a number?
      val = int(val)
    except ValueError:
      # if not then it must be a list of flags.
      val = _stringToListOfFlags(val)
    else:
      # if it is a number then it must either be a zero or a mode.
      if val != 0:
        val = _modeToListOfFlags(val)
    return val


class IntOrQuestionOrListOfFlags():
  """Parses int or question mark or list of strings
  
  int covers most cases
  question mark appears in some rare cases eg in exit_group
  
  List of flags appears only in fcntl which returns a hex followed by a
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
      raise Exception("Unexpected format when parsing value: " + val)
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
      raise Exception("Unexpected format when parsing value: " + val)
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
      raise Exception("Unexpected format when parsing value: " + val)
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
      raise Exception("Unexpected format when parsing value: " + val)
    try:
      # parse the port skipping the parts that wrap it.
      val = int(val[val.find('htons(')+len('htons('):val.find(')')])
    except ValueError:
      raise Exception("Unexpected format when parsing value: " + val)
    return val


class Pid():
  """
  Parses pid.
  """
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    # pid is given in the format 'pid=0'
    if val.find('pid=') == -1:
      raise Exception("Unexpected format when parsing value: " + val)
    try:
      # parse the pid skipping the label
      val = int(val[val.find('pid=')+len('pid='):])
    except ValueError:
      raise Exception("Unexpected format when parsing value: " + val)
    return val


class Groups():
  """
  Parses groups.
  """
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    # groups is given in the format 'groups=0000}'
    if val.find('groups=') == -1 or val.find('}') == -1:
      raise Exception("Unexpected format when parsing value: " + val)
    try:
      # parse the groups skipping the label
      val = int(val[val.find('groups=')+len('groups='):val.find('}')])
    except ValueError:
      raise Exception("Unexpected format when parsing value: " + val)
    return val


class MsgIov():
  """
  Parses message from msgiov.
  """
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    if val.find('=[{') == -1:
      raise Exception("Unexpected format when parsing value: " + val)
    return Str().parse(val[val.find("=[{")+len("=[{"):])


class MsgLen():
  """
  Parses msg len from msgiov.
  """
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    # msg len is given in the format '1234}]'
    if val.find('}]') == -1:
      raise Exception("Unexpected format when parsing value: " + val)
    try:
      # parse the pid skipping the label
      val = int(val[:val.find('}]')])
    except ValueError:
      raise Exception("Unexpected format when parsing value: " + val)
    return val


class MsgControllen():
  """
  Parses msg control len from msgiov.
  """
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    # msg control len is given in the format 'msg_controllen=0'
    if val.find('msg_controllen=') == -1:
      raise Exception("Unexpected format when parsing value: " + val)
    try:
      # parse the pid skipping the label
      val = int(val[val.find('msg_controllen=')+len('msg_controllen='):])
    except ValueError:
      raise Exception("Unexpected format when parsing value: " + val)
    return val


class MsgFlags():
  """
  Parses msg flags from msgiov.
  """
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    # msg flafs len is given in the format 'msg_flags=0}'
    if val.find('msg_flags=') == -1 or val.find('}') == -1:
      raise Exception("Unexpected format when parsing value: " + val)
    val = val[val.find('msg_flags=')+len('msg_flags='):val.find('}')]
    return ZeroOrListOfFlags().parse(val)


class StDev():
  """Parses st_dev of struct stat."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    # if the label is not found in the value parsing, raise an exception.
    if val.find('st_dev=') == -1:
      # if the syscall had an error the address of the struct is 
      # returned instead.
      if val.startswith('0x'):
        return Unknown()
      raise Exception("Unexpected format when parsing value: " + val)
 
    return val[val.find('st_dev=')+len('st_dev='):]


class StInt():
  """Parses st labels with type int of struct stat."""
  def __init__(self, label="", output=False):
    self.label = label
    self.output = output

  def parse(self, val):
    # if a label was not given, raise an exception.
    if(self.label == ""):
      raise Exception("Label not defined in StInt object.")
    # if the label is not found in the value parsing, raise an exception.
    if val.find(self.label+'=') == -1:
      raise Exception("Unexpected format when parsing value: " + val)
    try:
      # parse the value skipping the preceding label.
      val = int(val[val.find(self.label+'=')+len(self.label+'='):])
    except ValueError:
      raise Exception("Unexpected format when parsing StInt")
    return val


class StMode():
  """Parses st_mode of struct stat."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    if val.find('st_mode=') == -1:
      raise Exception("Unexpected format when parsing value: " + val)
    # parse the mode skipping the preceding label.
    val = val[val.find('st_mode=')+len('st_mode='):]
    return _stringToListOfFlags(val)


class StStr():
  """Parses st labels with type str of struct stat."""
  def __init__(self, label="", output=False):
    self.label = label
    self.output = output

  def parse(self, val):
    # if a label was not given, raise an exception.
    if(self.label == ""):
      raise Exception("Label not defined in StStr object.")
    # if the label is not found in the value parsing, raise an exception.
    if val.find(self.label+'=') == -1:
      raise Exception("Unexpected format when parsing value: " + val)
 
    return val[val.find(self.label+'=')+len(self.label+'='):]


class StSizeOrRdev():
  """Parses st_size or st_rdev of struct stat."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    # if the label is not found in the value parsing, raise an exception.
    if val.find('st_size=') != -1:
      # st size should have a number
      try:
        # parse the value skipping the preceding label.
        val = int(val[val.find('st_size=')+len('st_size='):])
      except ValueError:
        raise Exception("Unexpected format when parsing StSizeOrRdev")
    elif val.find('st_rdev=') != -1:
      # st_rdef parses a string
      val[val.find('st_rdev=')+len('st_rdev='):]
    else:
      raise Exception("Unexpected format when parsing value: " + val)
 
    return val


class StCtime():
  """Parses st_ctime of struct statfs."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    # if the st_ctime is not found in the value parsing, raise an exception.
    if val.find('st_ctime=') == -1 or val.find('}') == -1:
      raise Exception("Unexpected format when parsing value: " + val)

    return val[val.find('st_ctime=')+len('st_ctime='):val.rfind('}')]


class FType():
  """Parses f_type of struct statfs."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    if val.find('f_type=') == -1:
      # if the syscall had an error the address of the struct is 
      # returned instead.
      if val.startswith('0x'):
        return Unknown()
      raise Exception("Invalid type " + type(val))
    # parse the type skipping the preceding label.
    val = val[val.find('f_type=')+len('f_type='):]
    # val should be wrapped in double quotes.
    if not val.startswith('\"') or not val.endswith('\"'):
      raise Exception("Unexpected format when parsing value: " + val)
    # remove double quotes.
    val = val[1:-1]
    return val


class FInt():
  """Parses f labels with type int of struct statfs."""
  def __init__(self, label="", output=False):
    self.label = label
    self.output = output

  def parse(self, val):
    # if a label was not given, raise an exception.
    if(self.label == ""):
      raise Exception("Label not defined in FInt object.")
    # if the label is not found in the value parsing, raise an exception.
    if val.find(self.label+'=') == -1:
      raise Exception("Unexpected format when parsing value: " + val)
    try:
      # parse the value skipping the preceding label.
      val = int(val[val.find(self.label+'=')+len(self.label+'='):])
    except ValueError:
      raise Exception("Unexpected format when parsing FInt")
    return val


class FFsid():
  """Parses f_fsidof struct statfs."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    # if the label is not found in the value parsing, raise an exception.
    if val.find('f_fsid=') == -1:
      raise Exception("Unexpected format when parsing value: " + val)
    
    return val[val.find('f_fsid=')+len('f_fsid='):]


class FFrsize():
  """Parses f_frsize of struct statfs."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    # if the label is not found in the value parsing, raise an exception.
    if val.find('f_frsize=') == -1 or val.find('}') == -1:
      raise Exception("Unexpected format when parsing value: " + val)
    try:
      # parse the value skipping the preceding label.
      val = int(val[val.find('f_frsize=')+len('f_frsize='):val.rfind('}')])
    except ValueError:
      raise Exception("Unexpected format when parsing FFrsize")
    return val


class ChildStack():
  """Parses child stack."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    # if the label is not found in the value parsing, raise an exception.
    if val.find('child_stack=') == -1:
      raise Exception("Unexpected format when parsing value: " + val)
    return val[val.find('child_stack=')+len('child_stack='):]


class CloneFlags():
  """Parses clone flags stack."""
  def __init__(self, output=False):
    self.output = output

  def parse(self, val):
    # if the label is not found in the value parsing, raise an exception.
    if val.find('flags=') == -1:
      raise Exception("Unexpected format when parsing value: " + val)
    return ZeroOrListOfFlags().parse(val[val.find('flags=')+len('flags='):])


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
    'args': (ZeroOrListOfFlags(), ZeroOrListOfFlags(), ZeroOrListOfFlags()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int bind(int sockfd, const struct sockaddr *addr, socklen_t addrlen);
  # 
  # Example strace output:
  # 19176 bind(3, {sa_family=AF_INET, sin_port=htons(25588), sin_addr=inet_addr("127.0.0.1")}, 16) = 0
  # 19184 bind(3, {sa_family=AF_INET, sin_port=htons(25588), sin_addr=inet_addr("127.0.0.1")}, 16) = -1 EADDRINUSE (Address already in use)
  "bind": {
    'args': (Int(), SockFamily(), SockPort(), SockIP(), Int()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen);
  # 
  # Example strace output:
  # 19175 connect(5, {sa_family=AF_INET, sin_port=htons(25588), sin_addr=inet_addr("127.0.0.1")}, 16) = 0
  # 19262 connect(5, {sa_family=AF_INET, sin_port=htons(25588), sin_addr=inet_addr("127.0.0.1")}, 16) = -1 ECONNREFUSED (Connection refused)
  "connect": {
    'args': (Int(), SockFamily(), SockPort(), SockIP(), Int()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # ssize_t sendto(int sockfd, const void *buf, size_t len, int flags, const struct sockaddr *dest_addr, socklen_t addrlen);
  # 
  # Example strace output:
  # 19309 sendto(3, "Message for sendto.\0", 20, 0, {sa_family=AF_INET, sin_port=htons(25588), sin_addr=inet_addr("127.0.0.1")}, 16) = 20
  "sendto": {
    'args': (Int(), Str(), Int(), ZeroOrListOfFlags(), SockFamily(), 
             SockPort(), SockIP(), Int()),
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
  # ssize_t recvfrom(int sockfd, void *buf, size_t len, int flags, struct sockaddr *src_addr, socklen_t *addrlen);
  # 
  # Example strace output:
  # 19294 recvfrom(3, "Message for sendto.\0", 512, 0, {sa_family=AF_INET, sin_port=htons(40299), sin_addr=inet_addr("127.0.0.1")}, [16]) = 20
  "recvfrom": {
    'args': (Int(), Str(output=True), Int(), ZeroOrListOfFlags(), SockFamily(output=True), 
             SockPort(output=True), SockIP(output=True), Int(output=True)),
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
  # int getsockname(int sockfd, struct sockaddr *addr, socklen_t *addrlen);
  # 
  # Example strace output:
  # 19255 getsockname(3, {sa_family=AF_INET, sin_port=htons(0), sin_addr=inet_addr("0.0.0.0")}, [16]) = 0
  "getsockname": {
    'args': (Int(), SockFamily(output=True), SockPort(output=True), SockIP(output=True), Int(output=True)),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int   getpeername(int sockfd, struct sockaddr *addr, socklen_t *addrlen);
  # 
  # Example strace output:
  # 19252 getpeername(5, {sa_family=AF_INET, sin_port=htons(25588), sin_addr=inet_addr("127.0.0.1")}, [16]) = 0
  "getpeername": {
    'args': (Int(), SockFamily(output=True), SockPort(output=True), SockIP(output=True), Int(output=True)),
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
  # int accept(int sockfd, struct sockaddr *addr, socklen_t *addrlen);
  # 
  # Example strace output:
  # 19176 accept(3, {sa_family=AF_INET, sin_port=htons(42572), sin_addr=inet_addr("127.0.0.1")}, [16]) = 4
  "accept": {
    'args': (Int(), SockFamily(output=True), SockPort(output=True), SockIP(output=True), Int(output=True)),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int getsockopt(int sockfd, int level, int optname, void *optval, socklen_t *optlen);
  # 
  # Example strace output:
  # 19258 getsockopt(3, SOL_SOCKET, SO_TYPE, [1], [4]) = 0
  # 19258 getsockopt(3, SOL_SOCKET, SO_OOBINLINE, [0], [4]) = 0
  "getsockopt": {
    'args': (Int(), ZeroOrListOfFlags(), ZeroOrListOfFlags(), Int(output=True), Int(output=True)),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int setsockopt(int sockfd, int level, int optname, void *optval, socklen_t optlen);
  # 
  # Example strace output:
  # 19313 setsockopt(3, SOL_SOCKET, SO_REUSEADDR, [1], 4) = 0
  "setsockopt": {
    'args': (Int(), ZeroOrListOfFlags(), ZeroOrListOfFlags(), Int(), Int()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int shutdown(int sockfd, int how);
  # 
  # Example strace output:
  # 19316 shutdown(5, 0 /* receive */) = 0
  # 19316 shutdown(5, 2 /* send and receive */) = 0
  "shutdown": {
    'args': (Int(), Int()),
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
  # 19243 fstatfs(3, {f_type="EXT2_SUPER_MAGIC", f_bsize=4096, f_blocks=4553183, f_bfree=1457902, f_bavail=1226606, f_files=1158720, f_ffree=658673, f_fsid={-1853641883, -1823071587}, f_namelen=255, f_frsize=4096}) = 0
  "fstatfs": {
    'args': (Int(), FType(), FInt(label="f_bsize", output=True), 
             FInt(label="f_blocks", output=True), 
             FInt(label="f_bfree", output=True), 
             FInt(label="f_bavail", output=True), 
             FInt(label="f_files", output=True), 
             FInt(label="f_ffree", output=True), 
             FFsid(output=True), FInt(label="f_namelen", output=True), 
             FFrsize(output=True)),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int statfs(const char *path, struct statfs *buf);
  # 
  # Example strace output:
  # 19323 statfs("syscalls.txt", {f_type="EXT2_SUPER_MAGIC", f_bsize=4096, f_blocks=4553183, f_bfree=1458896, f_bavail=1227600, f_files=1158720, f_ffree=658713, f_fsid={-1853641883, -1823071587}, f_namelen=255, f_frsize=4096}) = 0
  "statfs": {
    'args': (Str(), FType(), FInt(label="f_bsize", output=True), 
             FInt(label="f_blocks", output=True), 
             FInt(label="f_bfree", output=True), 
             FInt(label="f_bavail", output=True), 
             FInt(label="f_files", output=True), 
             FInt(label="f_ffree", output=True), 
             FFsid(output=True), FInt(label="f_namelen", output=True), 
             FFrsize(output=True)),
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
  # int chdir(const char *path);
  # 
  # Example strace output:
  # 19217 chdir(".") = 0
  "chdir": {
    'args': (Str(),),
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
  # 19260 link("syscalls.txt", "syscalls.link") = -1 EEXIST (File exists)
  # 19260 link("hopefully_no_such_filename_exists.txt", "syscalls2.link") = -1 ENOENT (No such file or directory)
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
  # 19327 unlink("hopefully_no_such_filename_exists.txt") = -1 ENOENT (No such file or directory)
  "unlink": {
    'args': (Str(),),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int stat(const char *path, struct stat *buf);
  # 
  # Example strace output:
  # 10538 stat64("syscalls.txt", {st_dev=makedev(8, 6), st_ino=697814, st_mode=S_IFREG|0664, st_nlink=1, st_uid=1000, st_gid=1000, st_blksize=4096, st_blocks=0, st_size=0, st_atime=2013/03/06-00:17:54, st_mtime=2013/03/06-00:17:54, st_ctime=2013/03/06-00:17:54}) = 0
  # 19321 stat64("hopefully_no_such_filename_exists.txt", 0xbf8c7d50) = -1 ENOENT (No such file or directory)
  "stat": {
    'args': (Str(), StDev(output=True), 
             StInt(label="st_ino", output=True), StMode(output=True), 
             StInt(label="st_nlink", output=True), 
             StInt(label="st_uid", output=True), 
             StInt(label="st_gid", output=True), 
             StInt(label="st_blksize", output=True), 
             StInt(label="st_blocks", output=True), 
             StSizeOrRdev(output=True), 
             StStr(label="st_atime", output=True), 
             StStr(label="st_mtime", output=True), 
             StCtime(output=True)),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int fstat(int fd, struct stat *buf);
  # 
  # Example strace output:
  # 10605 fstat64(3, {st_dev=makedev(8, 6), st_ino=697814, st_mode=S_IFREG|0664, st_nlink=1, st_uid=1000, st_gid=1000, st_blksize=4096, st_blocks=0, st_size=0, st_atime=2013/03/06-00:17:54, st_mtime=2013/03/06-00:17:54, st_ctime=2013/03/06-00:17:54}) = 0
  # 32566 fstat64(0, {st_dev=makedev(0, 11), st_ino=8, st_mode=S_IFCHR|0620, st_nlink=1, st_uid=1000, st_gid=5, st_blksize=1024, st_blocks=0, st_rdev=makedev(136, 5), st_atime=2013/03/05-11:15:44, st_mtime=2013/03/05-11:15:44, st_ctime=2013/03/05-10:44:02}) = 0
  # 10605 fstat64(3, 0xbfb99fe0) = -1 EBADF (Bad file descriptor)
  "fstat": {
    'args': (Int(), StDev(output=True), 
             StInt(label="st_ino", output=True), StMode(output=True), 
             StInt(label="st_nlink", output=True), 
             StInt(label="st_uid", output=True), 
             StInt(label="st_gid", output=True), 
             StInt(label="st_blksize", output=True), 
             StInt(label="st_blocks", output=True), 
             StSizeOrRdev(output=True), 
             StStr(label="st_atime", output=True), 
             StStr(label="st_mtime", output=True), 
             StCtime(output=True)),
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
  # int getdents(unsigned int fd, struct linux_dirent *dirp, unsigned int count);
  # 
  # Example strace output:
  # 10917 getdents(3, {{d_ino=709301, d_off=2124195000, d_reclen=28, d_name="sendto.strace"} {d_ino=659266, d_off=2147483647, d_reclen=32, d_name="syscalls_functions.h"}}, 1024) = 60
  # 10917 getdents(3, {}, 1024) = 0
  "getdents": {
    'args': (Int(), Int()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int fcntl(int fd, int cmd, ... /* arg */ );
  # 
  # Example strace output:
  # 19239 fcntl64(3, F_GETFL) = 0 (flags O_RDONLY)
  # 19239 fcntl64(4, F_GETFL) = 0x402 (flags O_RDWR|O_APPEND)
  "fcntl": {
    'args': (Int(), ZeroOrListOfFlags(), ZeroOrListOfFlags()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # ssize_t recvmsg(int sockfd, struct msghdr *msg, int flags);
  # 
  # Example strace output:
  # recvmsg(4, {msg_name(12)={sa_family=AF_NETLINK, pid=0, groups=00000000}, msg_iov(1)=[{"\24\0\0\0\3\0\2\0\0170@P\275\v\0\0\0\0\0\0\1\0\0\0\10\0\1\0\177\0\0\1\10\0\2\0\177\0\0\1\7\0\3\0lo\0\0<\0\0\0\24\0\2\0\0170@P\275\v\0\0\2\30\200\0\2\0\0\0\10\0\1\0\300\250\1j\10\0\2\0\300\250\1j\10\0\4\0\300\250\1\377\t\0\3\0eth0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\223G\324\0\0\0\0\0\0\0\0\0\0\0\0\364\317\3\267\1\0\0\0\200<M\267\0\0\0\0\257\371\2\267\0\0\0\0\1\0\0\0\1\0\0\0\0\300\345\277\0\4\0\0<\310\345\277\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0<\310\345\277p\244\377\t\0\0\0\0\0K.\267\0\0\0\0\0\0\0\0\0\300\345\277\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\342\23:\267\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\1\0\0\0\0\0\0\0\0\0\0\0M\0017\267\364\17M\267\200\302\345\277\266\201:\267\364\17M\267\213\t7\267\0\0\0\0\200\357H\267\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\200\357H\267\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\377\377\377\377\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0 \0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\n\0\0\0\0\0\0\0\0\0\0\0h\303\345\277\0\0\0\0\0\0\0\0\0\0\0\0\3\0\0\0\377\377\377\377\0\0\0\0\0\0\0\0u\0\0\0\0\0\0\0\304\301\345\277\21P:\267\0\0\0\0M\6s\267\337\230\2\267\5\227q\267\0\0\0\0u\357H\267\0\0\0\0\0\0\0\0\0K.\267\6\0\0\0\334\226q\267\200\220\r\n8\276\345\277\364\177t\267\234\206\2\267\1\0\0\0\364u\r\n\234\fs\267\3\0\0\0002\0\0\0\377\377\377\377\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\364u\r\n\5\0\0\0008\0\0\0[\0\0\0\4\0\0\0i$\2\4\321\0\0\0\0\0\0\0\270\217\2\267\374+\1\0<-t\267\30\207\2\267\5\0\0\0\0@\1\0\0`\1\0\0\0\0\0\0\0\0\0\1\5gmail\3com\0\230\220\r\n\223\225q\267\250\221\2\267\230\223q\267\1\0\0\0\0\0\0\0\364\177t\267\230\220\r\n\364\177t\267\324\217\r\n\224\277\345\277P\277\345\277\311\16s\2670\277\345\277\230\223q\267\30\277\345\277t\217\r\n\0\0\0\0008v\r\n\1\0\0\0\0\0\0\0\1\0\0\0\30\216\r\n\0\0\0\0\0\0\0\0\271\35s\267\364\177t\267\0\0\0\0\230\220\r\n\370\277\345\277/\334r\267\340u\r\n\0\0\0\0\0\0\0\0\0\0\0\0\224\277\345\277\0\0\0\0\0\0\0\0\30\216\r\n\223\225q\267\0\0\0\0\0\0\0\0\21P:\267\0\0\0\0M\6s\267-,4\267\375ms\267\227+4\267\316ur\267\270\217\2\267\230\220\r\n\364\177t\267\227+4\267<\205t\267l\362r\267\377\377\377\377\204\215.\267(\0\0\0p\24M\267\4\211t\267\364\177t\267\30\216\r\n\1\0\0\0\0\0\0\0\213Rs\267\320\217\r\n8v\r\n\1\0\0\0\1\0\0\0\0\0\0\0(x\1\0\1\10\0\0\0\0\0\0\0\0\0\0\0\220q\267\250\224q\267P`\0\0\0\0\0\0\0\0\0\0\0\0\0\0\270\217\2\267\0\0\0\0@G\1\0\0\0\0\0\364\357q\267\0\1\0\0@\312\345\277X\310\345\277\240\266s\267\304\377\377\377\364\357q\267\0\300\345\277p\244\377\tX\310\345\277T\261q\267p\244\377\t\1\0\0\0d\314\345\277@\311\345\277\0\2\0\0\310J.\267\214\314\345\277\0\0\0\0\0\0\0\0\0\0\0\0\30\216\r\n\240\363r\267\320\360\201\200\0\1\0\2\0\0\0\0\5gmail\3com\0\0\1\0\1\300\f\0\1\0\1\0\0\0w\0\4\255\302+5\300\f\0\1\0\1\0\0\0w\0\4\255\302+6\0\326n\5\267\17\0\0\0\0\0\0\0\30\216\r\n\334\226q\267\0\2\0\0\177ELF\1\1\1\0\0\0\0\0\0\0\0\0\3\0\3\0\1\0\0\0\260&\0\0004\0\0\0hB\1\0\0\0\0\0004\0 \0\t\0(\0\37\0\36\0\6\0\0\0004\0\0\0004\0\0\0004\0\0\0 \1\0\0 \1\0\0\5\0\0\0\4\0\0\0\3\0\0\0\360\t\1\0\360\t\1\0\360\t\1\0\23\0\0\0\23\0\0\0\4\0\0\0\1\0\0\0\1\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\374+\1\0\374+\1\0\5\0\0\0\0\20\0\0\1\0\0\0\24:\1\0\24J\1\0\24J\1\0,\7\0\0\24.\0\0\6\0\0\0\0\20\0\0\2\0\0\0\324>\1\0\324N\1\0\324N\1\0\350\0\0\0\350\0\0\0\6\0\0\0\4\0\0\0\4\0\0\0T\1\0\0T\1\0\0T\1\0\0D\0\0\0D\0\0\0\4\0\0\0\4\0\0\0P\345td\4\n\1\0\4\n\1\0\4\n\1\0\304\3\0\0\304\3\0\0\4\0\0\0\4\0\0\0Q\345td\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\6\0\0\0\4\0\0\0R\345tdM\6s\267\265\230\2\2673\227q\267\354\5\0\0\364\177t\267\34\304\345\277\0\0\0\0\1\0\0\0\2\0\0\0\334\226q\267M\6s\267\257+4\2673\227q\267\330\206\2\267\1\0\0\0\364u\r\n\234\fs\267\34\304\345\277\2\0\0\0\353\226q\267\300\no\267\0\0\0\0\364\177t\267\24053\267\7\0\0\0\220\3662\267\234\fs\267$\0\0\0\4\0\0\0|\260\5\227\321\0\0\0\0\0\0\0\250\220\2\267\0\0\0\0\220\3662\267\30\207\2\2678\0\0\0[\0\0\0\v\0\0\0\273\225\223\34\363\3\0\0\1\0\0\0\370\2563\267xv\r\n<-t\2678>3\267\250\221\2\267\310\223q\267\0\0\0\0\0\0\0\0\0\0\0\0\1\0\0\0\f\7\0\0hv\r\n\20\vo\267\214\225q\267X\3213\267\370\222q\267\1\0\0\0\0\303\345\277t\217\r\n\0\0\0\0\364\177t\267\320\217\r\n\244\303\345\277`\303\345\277\311\16s\267@\303\345\277\370\222q\267(\303\345\277t\212t\267\0\0\0\0hv\r\n\1\0\0\0\0\0\0\0\1\0\0\0\30\216\r\n\0\0\0\0\0\0\0\0\34\304\345\277<\nA\267\364\17M\267\3\0\0\0x\303\345\277\250\220@\267\3\0\0\0\360\302\345\277\0\0\0\0\344N\0\0\244\303\345\277\0\0\0\0\0\0\0\0\30\216\r\n\214\225q\267\1\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\211\245B\267\0\0\0\0\0\20\0\0\370\2563\267\20\vo\267H%@P|]\347\33\177\0\0\1\16+0\33\377\377\377\377\253L\252\33\351\231B\267\364\17M\267\200<M\267\364\177t\267\30\216\r\n\26\264:\267\364\177t\267SSs\267\320\217\r\nhv\r\n\1\0\0\0\1\0\0\0\0\0\0\0\0\0\0\0\0\0q\267\316$\0\0\244\201\0\0\0\220q\267\250\224q\267,`\0\0\0\0\0\0\0\0\0\0\0\0\0\0\370\2563\267\0\20\0\0\10\0\0\0H%@P\364\357q\267\214\314\345\277\0K.\267X\310\345\277\240\266s\267\2\0\0\0\2406<\267\4\0\0\0\30\216\r\n\0K.\267\216\260q\267p\244\377\t.\0\0\0\0\0\0\0\364\177t\267\30\216\r\n\374\377\377\377\1\0\0\0\204_s\267\364\325\345\277\0\326\345\277\0\0\0\0\0\0\0\0\0\0\0\0\2\0\0\0\364\325\345\277\250\220\2\2671\304\345\277\0\0\0\0n\0\0\0\1\0\0\0\320\305\345\277\10\0\0\0\310\304\345\277\226\237s\267\0\326\345\277\320\217\r\n\1\0\0\0\0\0\0\0\30\216\r\n\230\220\r\n\30\216\r\n\32\236s\267\0\0\0\0\0\0\0\200\0\0\0\0\1\0\0\0\244\325\v\nM\6s\267\257+4\267\311\4r\267P\304\345\277`\304\345\277@\304\345\277\0\0\0\0\1\330\v\n\1\0\0\200\1\0\0\0\2\0\0\0t\217\r\n\4\0\0\0\30\216\r\n\4\0\0\0\220\3662\267\234\fs\267\10\306\345\277\214\5s\267\303\225q\267\0\310\345\277\30\306\345\277\277\\s\267\320\305\345\277\0\0\0\0000&3\267\7\0\0\0\374J.\267\364\305\345\277\370\305\345\277\364\177t\267\360\221q\267\0\0\0\0\364u\r\n\234\fs\267\364\177t\267\376\377\377\377\344\204t\267\30\306\345\277\320\304\345\277\236\\s\267\1\0\0\0\364u\r\n \371\f\n\20\vo\267\322\3r\267\4\0\0\0\30h\251\344\r\0\0\0h\1r\267H\224q\267\0\0\0\0<-t\267\10\222q\267d\306\345\277 \306\345\277\311\16s\267H\224q\267\1\0\0\0\2\0\0\0\0\0\0\0\0\0\0\0\30\216\r\n\0\310\345\277\250\224q\267\0\0\0\0\0\0\0\0P\306\345\277\311\16s\2670\306\345\277\364\177t\267\350\217\r\n\334\307\345\277h\306\345\277\311\16s\267H\306\345\277\0\0\0\0000\306\345\277t\217\r\n\0\0\0\0\0\0\0\0\2\0\0\0\0\0\0\0\0\0\0\0\30\216\r\n\27\274B\267A=E\267\300\307\345\277\1\0\0\200\27\274B\267A=E\267\30\216\r\n\0\0\0\0\2\0\0\0\364\325\345\277\0\0\0\0\0\0\0\0\334\307\345\277\364\17M\0\0\0\0\0\30\216\r\n\0\310\345\277\364\17M\267\200\307\345\277\300\307\345\277\30\310\345\277A=E\267\300\307\345\277\1\0\0\200\27\274B\267\376\377\377\377H\224q\267\30\216\r\n\0\326\345\277\277\\s\267p\307\345\277\364\177t\267\377\377\377\377\277\\s\267\200\307\345\277\0\0\0\0\200\330\v\n\364\17M\267\240|t\267\320\307\345\277X\310\345\277\262=E\267\350\217\r\n\0\0\0\0\0\0\0\0\2\0\0\0\0\0\0\0\240|t\267\300\307\345\277\30\310\345\277\364\177t\267\0\0\0\0]\346H\267\277\\s\267\320\307\345\277\0\0\0\0p\244\377\t\310\377\377\377\374J.\267\244\307\345\277\250\307\345\277\257\307\345\277p\244\377\t\310\377\377\377\0\0\0\0\375\22r\267\364\177t\267\240|t\267]\346H\267X\310\345\277\240\306\345\277\236\\s\267\0\0\0\0\21P:\267\244\307\345\277\311\360\5\267\0\0\0\0\0\0\0\0.\f\4\267x\1\0\0\0\0\0\0\0\0\0\0\0\0\0\0\20'\0\0\20\0\0\0\0\0\0\0W\\s\267\364\17M\267\240|t\2677>E\267\340<E\267\200\307\345\277\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\2\0\0\0008\0\0\0[\0\0\0\0\0\0\0\0\0\0\0|\0\0\0\7>E\267\364\17M\267\0\0\0\0\0\0\0\0W\\s\267\364\17M\267\240|t\2677>E\267P=E\267\320\307\345\277\27\274B\267\30\216\r\n\364\17M\267\364\17M\2670\34\r\n\27\274B\267\300\307\345\277\0\0\0\0\0\0\0\0\364\17M\0\7>E\267\364\17M\267\0\310\345\277(?E\267libnss_dns.so.2\0\30\216\r\n\0\310\345\277\30\216\r\nH\224q\267\364\17M\267\366>E\267\364\17M\267\340\303B\267\30\216\r\n\0\310\345\277\300\307\345\277\21P:\267_nss_dns_gethostbyname2_r\0\345\277\201\303B\267]\346H\267\2\0\0\0\200\266B\267\234\256B\267\0\0\0\0\20'\0\0008\0\0\0p\24M\267x\24M\267\0\0\0\0000\0\0\0\7\0\0\0\0\0\0\0H\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\7\0\0\0008\0\0\0[\0\0\0n\0\0\0w\0\0\0|\0\0\0\0\0\0\0\200\252B\267\0\0\0\0\364\17M\267@\24M\267\24\341\v\n0\0\0\0<}:\267d\314\345\277]\346H\267\0\0\0\0\350\310\345\277\1\0\0\0\0\0\0\0\214\314\345\277\2\0\0\0\214\314\345\277Hy3\267\0\0\0\0\364\17M\267\200\313\345\277\24\341\v\n\250\314\345\277\261/?\2670\0\0\0<\312\345\277\4\0\0\0\1\0\0\0\0\3672\267\20\vo\267l\37\5\10\364\17M\267\0\2\0\0p\244\377\t\250\314\345\277\31;?\267\0\0\0\0\2\0\0\0\2\0\0\0\255\302+6\0\2\0\0\210\314\345\277\214\314\345\277\0\0\0\0\0\0\0\0\234\311\345\277,\312\345\277\0\2\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\2@\311\345\277\0\0\0\0ff02::2\0ip6-allrouters\0\0\0-loopback\0\0n\311\345\277\0\0\0\0 capable hosts\n\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0 \0\0\364\17M\267 \312\345\277\262\222@\267\364\17M\267\224\22:\267\3\0\0\0\0\20\0\0\10nA\267\0\20\0\0\210G\r\n\364\17M\267\210G\r\n\21119\267\210G\r\n\0\360\5\267\0\0\6\267\10\313\345\277\0\0\0\0\0068A\267\364\17M\267\223\317C\267\0\0\0\0<\312\345\277\0\0\0\0gmai", 4096}], msg_controllen=0, msg_flags=0}, 0) = 20
  "recvmsg": {
    'args': (Int(), SockFamily(output=True), SockPort(output=True), 
             SockIP(output=True), MsgIov(output=True), 
             MsgLen(output=True), MsgControllen(output=True),
             MsgFlags(output=True), ZeroOrListOfFlags()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # ssize_t sendmsg(int sockfd, const struct msghdr *msg, int flags);
  # 
  # Example strace output:
  # 19307 sendmsg(3, {msg_name(16)={sa_family=AF_INET, sin_port=htons(25588), sin_addr=inet_addr("127.0.0.1")}, msg_iov(1)=[{"Message for sendmsg.\0", 21}], msg_controllen=0, msg_flags=0}, 0) = 21
  "sendmsg": {
    'args': (Int(), SockFamily(), SockPort(), 
             SockIP(), MsgIov(), 
             MsgLen(), MsgControllen(),
             MsgFlags(), ZeroOrListOfFlags()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
  },
  # int clone(int (*fn)(void *), void *child_stack, int flags, void *arg, ... /* pid_t *ptid, struct user_desc *tls, pid_t *ctid */ );
  # 
  # Example strace output:
  # 7122 clone(child_stack=0xb7507464, flags=CLONE_VM|CLONE_FS|CLONE_FILES|CLONE_SIGHAND|CLONE_THREAD|CLONE_SYSVSEM|CLONE_SETTLS|CLONE_PARENT_SETTID|CLONE_CHILD_CLEARTID, parent_tidptr=0xb7507ba8, {entry_number:6, base_addr:0xb7507b40, limit:1048575, seg_32bit:1, contents:0, read_exec_only:0, limit_in_pages:1, seg_not_present:0, useable:1}, child_tidptr=0xb7507ba8) = 7123
  # 
  "clone": {
    'args': (ChildStack(), CloneFlags(), SkipRemaining()),
    'return': (IntOrQuestionOrListOfFlags(), NoneOrStr())
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
  
  # A a list of flags can also contain a mode in its numeric value.
  # Example:
  # 19243 fstat64(3, {st_mode=S_IFREG|0644, st_size=98710, ...}) = 0
  # go through all flags and translate numeric mode to flads.
  for flag in flags_string.split("|"):
    try:
      flag_int = int(flag.strip('0'))
    except ValueError:
      flags_list.append(flag)
    else:
      # numeric mode within a list of flags. Example: S_IFREG|0755
      # translate to flags.
      flags_list += _modeToListOfFlags(flag_int)
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
  
  # if the mode is zero then return zero instead of an empty list.
  if mode == 0:
    return mode

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
      entity = int(mode_character)
      
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
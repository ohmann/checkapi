###################################################
# Classes that define the expected argument types #
###################################################
class Skip():
  """Indicates skip argument."""


class SkipRemaining():
  """Indicates skip all remaining arguments."""


class Int():
  """Allows int."""

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
      raise Exception("Invalid type %s" % type(val))

    return val


class ListOfStr():
  """Allows list of strings."""

  def parse(self, val):
    return val.split("|")


class IntOrListOfStr():
  """Allows int or list of HANDLED_FLAGS."""

  def parse(self, val):
    try:
      val = int(val)
    except:
      val = val.split("|")
    
    return val


class Str():
  """Allows str or unicode."""
 
  def parse(self, val):
    if not (type(val) is str or type(val) is unicode):
      raise Exception("Invalid type %s" % type(val))

    if val.endswith('\"...'):
      val = val[:val.rfind('...')]

    if not val.startswith('\"') or not val.endswith('\"'):
      raise Exception("Invalid type %s" % type(val))
    
    # remove double quotes from start and end of string.
    val = val[1:-1]

    # replace special characters.
    val = val.replace("\\n", "\n")
    val = val.replace("\\r", "\r")
    val = val.replace("\\t", "\t")
    val = val.replace("\\0", "\0")
    
    return val


class NoneOrStr():
  """Allows a NoneType or a string."""
 
  def parse(self, val):
    if val is not None and not (type(val) is str or type(val) is unicode):
      raise Exception("Invalid type %s" % type(val))


class SockFamily():
  """Allows sa_family of sockaddr."""

  def parse(self, val):
    val = val[val.find('sa_family=')+len('sa_family='):]
    return val.split("|")



class SockIP():
  """Allows sin_addr of sockaddr."""

  def parse(self, val):
    val = val[val.find('inet_addr(\"')+len('inet_addr(\"'):val.find('\")')]
    return val



class SockPort():
  """Allows sin_port of sockaddr."""

  def parse(self, val):
    try:
      val = val[val.find('htons(')+len('htons('):val.find(')')]
    except:
      raise Exception("Invalid type %s" % type(val))
    
    return val



# Expected arguments per syscall.
HANDLED_SYSCALLS_INFO = {
  "socket": {
    'args': (ListOfStr(), ListOfStr(), ListOfStr()),
    'return': (Int(), Str())
  },
  "bind": {
    'args': (Int(), SockFamily(), SockPort(), SockIP(), Int()),
    'return': (Int(), Str())
  },
  "connect": {
    'args': (Int(), SockFamily(), SockPort(), SockIP(), Int()),
    'return': (Int(), Str())
  },
  "sendto": {
    'args': (Int(), Str(), Int(), IntOrListOfStr(), SockFamily(), 
             SockPort(), SockIP(), Int()),
    'return': (Int(), Str())
  },
  "send": {
    'args': (Int(), Str(), Int(), IntOrListOfStr()),
    'return': (Int(), Str())
  },
  "recvfrom": {
    'args': (Int(), Str(), Int(), IntOrListOfStr(), SockFamily(), 
             SockPort(), SockIP(), Int()),
    'return': (Int(), Str())
  },
  "recv": {
    'args': (Int(), Str(), Int(), IntOrListOfStr()),
    'return': (Int(), Str())
  },
  "getsockname": {
    'args': (Int(), SockFamily(), SockPort(), SockIP(), Int()),
    'return': (Int(), Str())
  },
  "getpeername": {
    'args': (Int(), SockFamily(), SockPort(), SockIP(), Int()),
    'return': (Int(), Str())
  },
  "listen": {
    'args': (Int(), Int()),
    'return': (Int(), Str())
  },
  "accept": {
    'args': (Int(), SockFamily(), SockPort(), SockIP(), Int()),
    'return': (Int(), Str())
  },
  "getsockopt": {
    'args': (Int(), IntOrListOfStr(), IntOrListOfStr(), Int(), Int()),
    'return': (Int(), Str())
  },
  "setsockopt": {
    'args': (Int(), IntOrListOfStr(), IntOrListOfStr(), Int(), Int()),
    'return': (Int(), Str())
  },
  "shutdown": {
    'args': (Int(), Int()),
    'return': (Int(), Str())
  },
  "close": {
    'args': (Int(), Int()),
    'return': (Int(), Str())
  },
  "fstatfs": {
    'args': (Int(), SkipRemaining()),
    'return': (Int(), Str())
  },
  "statfs": {
    'args': (Str(), SkipRemaining()),
    'return': (Int(), Str())
  },
  "access": {
    'args': (Str(), IntOrListOfStr()),
    'return': (Int(), Str())
  },
  "chdir": {
    'args': (Str(),),
    'return': (Int(), Str())
  },
  "mkdir": {
    'args': (Str(), IntOrListOfStr()),
    'return': (Int(), Str())
  },
  "rmdir": {
    'args': (Str(),),
    'return': (Int(), Str())
  },
  "link": {
    'args': (Str(), Str()),
    'return': (Int(), Str())
  },
  "symlink": {
    'args': (Str(), Str()),
    'return': (Int(), Str())
  },
  "unlink": {
    'args': (Str(),),
    'return': (Int(), Str())
  },
  "stat": {
    'args': (Str(), SkipRemaining()),
    'return': (Int(), Str())
  },
  "fstat": {
    'args': (Int(), SkipRemaining()),
    'return': (Int(), Str())
  },
  "open": {
    'args': (Str(), IntOrListOfStr(), IntOrListOfStr()),
    'return': (Int(), Str())
  },
  "creat": {
    'args': (Str(), IntOrListOfStr()),
    'return': (Int(), Str())
  },
  "lseek": {
    'args': (Int(), Int(), IntOrListOfStr()),
    'return': (Int(), Str())
  },
  "read": {
    'args': (Int(), Str(), Int()),
    'return': (Int(), Str())
  },
  "write": {
    'args': (Int(), Str(), Int()),
    'return': (Int(), Str())
  },
  "dup": {
    'args': (Int(),),
    'return': (Int(), Str())
  },
  "dup2": {
    'args': (Int(), Int()),
    'return': (Int(), Str())
  },
  "dup3": {
    'args': (Int(), Int(), IntOrListOfStr()),
    'return': (Int(), Str())
  },
  "getdents": {
    'args': (Int(), Skip(), Int()),
    'return': (Int(), Str())
  },
  "fcntl": {
    'args': (Int(), IntOrListOfStr(), IntOrListOfStr()),
    'return': (Int(), Str())
  }
}
"""
<Program>
  parser_truss_calls.py

<Started>
  February 2013

<Author>
  Savvas Savvides <savvas@nyu.edu>

<Purpose>
  

"""

from parser_helper_calls import *


DEBUG = False




def parse_trace(fh):
  # this list will hold all the parsed syscalls
  actions = []
  
  # process each line
  while True:
    line = fh.readline()
    if not line:
      break

    line = line.strip()
    
    if DEBUG:
      print line
    
    # Ignore incomplete syscall lines without '(', ')', and '='
    if (line.find('(') == -1 or line.find(')') == -1 or 
        (line.find('=') == -1 and line.find('Err') == -1)):
      continue

    # Ignore syscalls that are sleeping.
    # When syscalls "wake up" they are printed in full so we don't
    # have to keep track of the sleeping syscalls.
    if line.find('(sleeping...)') != -1:
      continue
    
    # Get the syscall name.
    if len(line[:line.find('(')].split()) > 1:
      syscall_name = line[:line.find('(')].split()[-1]
    else:
      syscall_name = line[:line.find('(')]

    # Get the syscall parameters.
    parameterChunk = line[line.find('(')+1:line.rfind(')')].strip()
    parameters = parameterChunk.split(", ")
    
    # if the syscall is getdents, keep only the first and last parameters.
    if syscall_name.startswith("getdents"):
      parameters = [parameters[0], parameters[-1]]

    # if the syscall is getdents, keep only the first two paramenters
    if syscall_name.startswith("fcntl"):
      parameters = [parameters[0], parameters[1]]
    
    # Fix errors from split on messages
    mergeQuoteParameters(parameters)
    
    # Get the return part.
    trussResult = line[line.rfind(')')+1:]
    if trussResult.find("=") != -1:
      trussResult = line[line.rfind('=')+2:].strip()
    else:
      trussResult = line[line.rfind('Err'):].strip()

    # Is the result a status number or error message?
    spaced_results = trussResult.split()
    if len(spaced_results) > 1:
      trussResult = spaced_results[0]
    # truss prints Err#INT for errors where INT is the error number.
    if trussResult.startswith("Err"):
      trussResult = -1

    # in case of an error include the error name as well.
    if trussResult == -1 and len(spaced_results) > 1:
      trussResult = [trussResult, spaced_results[1]]
    else:
      # if no error, use None as the second return value
      trussResult = [trussResult, None]

    # translate arguments to the format expected by the IR
    syscall_name = _translate_truss_arguments(fh, syscall_name, parameters, 
                                                trussResult)
    

    action = parse_syscall(syscall_name, parameters, trussResult)
    
    if action != UNIMPLEMENTED_ERROR:
      actions.append(action)
  
  # display all skipped syscall_names.
  if(DEBUG):
    print "\nSkipped System Calls"
    for skipped in SKIPPED_SYSCALLS:
      print skipped + ": " + str(SKIPPED_SYSCALLS[skipped])
  
  return actions

"""
posix_intermediate_representation expects a slightly different argument format 
than the format used in truss. This IR format was heavily based on the format 
used in strace. Hence a translation step must be performed before the IR can 
parse these arguments.
"""
def _translate_truss_arguments(fh, syscall_name, args, result):
  # handle any 'syscall64' the exact same way as 'syscall'
  # eg fstat64 will be treated as if it was fstat
  if syscall_name.endswith('64'):
    syscall_name = syscall_name[:syscall_name.rfind('64')]
  # same for syscall4
  if syscall_name.endswith('4'):
    syscall_name = syscall_name[:syscall_name.rfind('4')]
  
  # these system calls prepend an unnecessary argument. Remove it and rename the
  # syscalls.
  if syscall_name == "xstat":
    syscall_name = "stat"
    args.pop(0)
  if syscall_name == "fxstat":
    syscall_name = "fstat"
    args.pop(0)
    
  
  # Translate individual syscalls.
  if syscall_name == "so_socket":
    # so_socket(PF_INET, SOCK_STREAM, IPPROTO_IP, "", SOV_DEFAULT) = 3
    # keep only the first three arguments.
    keep = 3
    for index in range(keep, len(args)):
      args.pop(keep)
    # rename to socket
    syscall_name = "socket"
  
  elif (syscall_name == "bind" or syscall_name == "connect" or 
        syscall_name == "accept" or syscall_name == "getsockname" or 
        syscall_name == "getpeername" or syscall_name == "setpeername"):
    # 1648: bind(3, 0x080474F0, 16, SOV_SOCKBSD)    = 0
    # 1648:   AF_INET  name = 0.0.0.0  port = 25588
    # 1815/1:   connect(5, 0x080474F0, 16, SOV_DEFAULT)   = 0
    # 1815/1:     AF_INET  name = 0.0.0.0  port = 25588
    # 1698/1:   connect(5, 0x080474F0, 16, SOV_DEFAULT)   Err#146 ECONNREFUSED
    # 1698/1:     AF_INET  name = 0.0.0.0  port = 25588
    # 3222/1:   getpeername(5, 0x080474C0, 0x080474D8, SOV_DEFAULT) = 0
    # 3222/1:     AF_INET  name = 127.0.0.1  port = 25588
    # 3217: getsockname(3, 0x080474C0, 0x080474DC, SOV_DEFAULT) = 0
    # 3217:     AF_INET  name = 127.0.0.1  port = 25588
    # keep only the first three arguments.
    keep = 3
    for index in range(keep, len(args)):
      args.pop(keep)

    # read family ip and port from the next line.
    (afamily, ip, port) = _get_sockaddr(fh, result)
    # replace argument 1 with afamily. Before this replacement,
    # argument 1 holds the address of the sockaddr structure.
    args[1] = afamily
    # Only include port and ip if the safamily is not empty
    if afamily != "sa_family=":
      # include port and ip in the arguments.
      args.insert(2, port)
      args.insert(3, ip)

  elif syscall_name == "sendto" or syscall_name == "recvfrom":
    # 3323: sendto(3, 0x08059C1D, 20, 0, 0x080474F0, 16)  = 20
    # 3323:    M e s s a g e   f o r   s e n d t o .\0
    # 3323:   AF_INET  to = 0.0.0.0  port = 25588
    # 3012: sendto(4, 0x0808B9E0, 64, 32768, 0x0806AA90, 16) = 64
    # 3012: \b\019 -\f j\0\0909D14 Q 7 w\v\0\b\t\n\v\f\r0E0F1011121314151617
    # 3012: 18191A1B1C1D1E1F   ! " # $ % & ' ( ) * + , - . / 0 1 2 3 4 5 6 7
    # 3012: AF_INET  to = 173.194.73.105  port = 0
    if args[1].startswith("0x"):
      # if argument 1 starts with 0x it means that the address of the
      # string is given rather than the string itself. The latter is
      # hence provided in the next line.
      args[1] = _get_message(fh, result[0]) # replace string address
    
    # read family ip and port from the next line.
    (afamily, ip, port) = _get_sockaddr(fh, result)
    # replace argument 4 with afamily. Before this replacement,
    # argument 4 holds the address of the sockaddr structure.
    args[4] = afamily
    # Only include port and ip if the safamily is not empty
    if afamily != "sa_family=":
      # include port and ip in the arguments.
      args.insert(5, port)
      args.insert(6, ip)

  elif syscall_name == "send" or syscall_name == "recv":
    # 3340/1:   send(5, "\0\0 cF4", 4, 0)     = 4
    # 3340/1:   send(5, 0x08059BF1, 23, 1)      = 23
    # 3340/1:      N o n e   s h a l l   b e   r e v e a l e d\0
    if args[1].startswith("0x"):
      # if argument 1 starts with 0x it means that the address of the
      # string is given rather than the string itself. The latter is
      # hence provided in the next line.
      args[1] = _get_message(fh, result[0]) # replace string address

  elif syscall_name == "listen" or syscall_name == "shutdown":
    # 1698/2:   listen(3, 5, SOV_DEFAULT)     = 0
    # 1698/2:   shutdown(5, SHUT_RD, SOV_DEFAULT)     = 0
    # keep only the first two arguments.
    keep = 2
    for index in range(keep, len(args)):
      args.pop(keep)

  elif syscall_name == "read" or syscall_name == "write":
    # 19477: read(3, "Sample output text\n", 20) = 19
    # 19477: write(1, 0xD1E46BA4, 24)     = 24
    # 19477:    w w w . g o o g l e . c o m   i s   a l i v e\n
    if args[1].startswith("0x"):
      args[1] = _get_message(fh, result[0]) # replace string address
  
  elif syscall_name == "getsockopt" or syscall_name == "setsockopt":
    # 3201/2:   getsockopt(20, SOL_SOCKET, SO_RCVBUF, 0xD169FF10, 0xD169FF0C, SOV_XPG4_2) = 0
    # setsockopt(4, SOL_SOCKET, SO_RCVBUF, 0x080474C4, 4, SOV_DEFAULT) = 0
    # keep only the first five arguments.
    keep = 5
    for index in range(keep, len(args)):
      args.pop(keep)

  elif syscall_name == "fstat" or syscall_name == "stat":
    # 3201/1:   fstat64(6, 0x080472E0)        = 0
    # 3201/1:       d=0x00780000 i=185862 m=0100644 l=1  u=0     g=0     sz=56
    # 3201/1:     at = Feb  8 01:44:59 EST 2013  [ 1360305899.475745000 ]
    # 3201/1:     mt = Feb  7 13:38:48 EST 2013  [ 1360262328.015187000 ]
    # 3201/1:     ct = Feb  7 13:38:48 EST 2013  [ 1360262328.373997000 ]
    # 3201/1:       bsz=8192  blks=2     fs=ufs
    #
    # 3201/2:   fstat64(1, 0xD169E6C0)        = 0
    # 3201/2:       d=0x049C0000 i=12582924 m=0020620 l=1  u=0     g=7     rdev=0x00600004
    # 3201/2:     at = Feb  8 01:45:03 EST 2013  [ 1360305903.000000000 ]
    # 3201/2:     mt = Feb  8 01:45:04 EST 2013  [ 1360305904.000000000 ]
    # 3201/2:     ct = Feb  7 14:05:36 EST 2013  [ 1360263936.000000000 ]
    # 3201/2:       bsz=8192  blks=0     fs=devfs
    #
    # 3212: stat64("/savvas/syscalls", 0x08047160)    = 0
    # 3212:     d=0x00780000 i=299671 m=0100755 l=1  u=0     g=0     sz=58140
    # 3212:   at = Feb  8 01:48:08 EST 2013  [ 1360306088.906915000 ]
    # 3212:   mt = Feb  5 01:26:31 EST 2013  [ 1360045591.150428000 ]
    # 3212:   ct = Feb  5 01:26:31 EST 2013  [ 1360045591.150428000 ]
    # 3212:     bsz=8192  blks=114   fs=ufs
    #
    # stat64("/usr/lib/dns/libcrypto.so.0.9.7", 0x08046A00) Err#2 ENOENT
    (st_dev, st_ino, st_mode, st_nlink, st_uid, st_gid,
     st_blksize, st_blocks, st_size_or_rdev_value, st_atime,
     st_mtime, st_ctime) = _get_stat(fh, result)
    
    args[1] = st_dev # replace structure address
    args.insert(2, st_ino)
    args.insert(3, st_mode)
    args.insert(4, st_nlink)
    args.insert(5, st_uid)
    args.insert(6, st_gid)
    args.insert(7, st_blksize)
    args.insert(8, st_blocks)
    args.insert(9, st_size_or_rdev_value)
    args.insert(10, st_atime)
    args.insert(11, st_mtime)
    args.insert(12, st_ctime)

  elif syscall_name == "fstatvfs" or syscall_name == "statvfs":
    # strace example:
    # 7196  fstatfs(3, {f_type="EXT2_SUPER_MAGIC", f_bsize=4096, 
    #                   f_blocks=4553183, f_bfree=1919236, f_bavail=1687940, 
    #                   f_files=1158720, f_ffree=658797, 
    #                   f_fsid={-1853641883, -1823071587}, 
    #                   f_namelen=255, f_frsize=4096}) = 0
    #
    # truss example:
    # 2373: fstatvfs(3, 0x08047460)       = 0
    # 2373:   bsize=8192       frsize=1024      blocks=8139687  bfree=3830956  
    # 2373:   bavail=3749560   files=984256     ffree=797256    favail=797256   
    # 2373:   fsid=0x780000    basetype=ufs     namemax=255
    # 2373:   flag=ST_NOTRUNC
    # 2373:   fstr=""

    (f_type, f_bsize, f_blocks, f_bfree, f_bavail, f_files, f_ffree, f_fsid, 
     f_namelen, f_frsize) = _get_statvfs(fh, result)
    
    args[1] = f_type # replace structure address
    args.insert(2, f_bsize)
    args.insert(3, f_blocks)
    args.insert(4, f_bfree)
    args.insert(5, f_bavail)
    args.insert(6, f_files)
    args.insert(7, f_ffree)
    args.insert(8, f_fsid)
    args.insert(9, f_namelen)
    args.insert(10, f_frsize)

    if syscall_name == "fstatvfs":
      syscall_name = "fstatfs"
    else:
      syscall_name = "statfs"

  
  elif syscall_name == "fcntl":
    if args[1] == "F_GETFL":
      # translate return value from int to flags
      flags = _translate_fcntl(result[0])
      
      # remove the current result[0]
      result.pop(0)
      # and replace it with the flags
      result.insert(0, flags)

    # TODO: deal with different cmd options.

  elif (syscall_name == "close" or syscall_name == "access" or
        syscall_name == "chdir" or syscall_name == "rmdir" or 
        syscall_name == "mkdir" or syscall_name == "link" or
        syscall_name == "symlink" or syscall_name == "unlink" or
        syscall_name == "open" or syscall_name == "lseek" or
        syscall_name == "dup" or syscall_name == "dup2"):
    # 1698: close(3)          = 0
    # 1600: access("syscalls.txt", F_OK)          = 0
    # 1621: chdr(".")          = 0
    # 1621: rmdir("sycalls_dir")          = 0
    # 1621: mkdir("sycalls_dir", 0775)          = 0
    pass

  """
  I need to add support for:
    statvfs
    fstatvfs
    fcntl -- return value 
    recvmsg
    sendmsg
    clone
    ioctl
    select
    poll
  """

  return syscall_name



#####################
# Helper Functions. #
#####################
def _get_sockaddr(fh, result):
  """
  Returns a tuple (family, ip, port)

  The sockaddr structure is given in the line following the current line. If the
  line is of the expected format, the line is read and the information returned 
  in a tuple. Otherwise undo reading the next line.
  """
  
  # initialize to empty strings
  family = ""
  ip = ""
  port = ""
  
  # if the syscall returned an error, don't parse the sockaddr
  # structure
  if result[0] != -1:
    last_file_pos = fh.tell()
    line = fh.readline()
    # the expected format must contain the label "port =" and either
    # "name =" or "to =" or "from ="
    if ((line.find("name =") != -1 or line.find("to =") != -1 or 
         line.find("from =") != -1) and line.find("port =") != -1):
      # ip can be labeled as "name =" or "to =" or "from ="
      if line.find("name =") != -1:
        family = line[line.find(":")+1:line.find("name =")].strip()
        ip = line[line.find("name =")+6:line.find("port =")].strip()
      elif line.find("from =") != -1:
        family = line[line.find(":")+1:line.find("from =")].strip()
        ip  = line[line.find("from =")+6:line.find("port =")].strip()
      else:
        family = line[line.find(":")+1:line.find("to =")].strip()
        ip  = line[line.find("to =")+4:line.find("port =")].strip()
      port = line[line.find("port =")+6:].strip()
    else:
      # undo reading so that the next line will be read in the next
      # iteration.
      fh.seek(last_file_pos)
  
  # translate to the format expected by the IR.
  family = "sa_family=" + family
  ip = 'sin_addr=inet_addr("' + ip + '")'
  port = "sin_port=htons(" + port + ")"

  return (family, ip, port)


def _get_message(fh, msglen):
  """Returns the message

  The message is given in the line (or maybe multiple lines)
  following the current line. If the length of the line(s) read match
  the length of the expected message the message is wrapped in double
  quotes and returned. Otherwise an exception is raised.
  """
  
  message = ""
  try:
    msglen = int(msglen)
  except ValueError:
    raise Exception("Unexpected msglen format.")
  
  previousLine = ""
  # if the syscall returned an error, don't parse the message
  if msglen > 0:
    while len(message) < msglen:
      line = fh.readline()
      if not line:
        raise Exception("Reached end of line while trying to read " + 
                        "message")
      
      # remove pid from message
      colon_position = line.find(":")
      if(colon_position == 4 and line[:colon_position].isdigit() or
         colon_position == 6 and line[:colon_position-2].isdigit()):
        line = line[colon_position+1:]
      
      # Remove the whitespace from the start of the line. The maximum
      # length of a line can be 64 characters.
      if len(line) > 64:
        line = line[len(line)-64:]
      else:
        line = line.strip()
      
      # each character in the message is stupidly space padded.
      replace_string = "#*"
      while line.find(replace_string) != -1:
        replace_string += "*"
      # replace actual spaces with replace_string. An actual space is
      # preceded with another space hence a set of two consequent 
      # spaces in a row represents an actual space.
      line = line.replace("  ", replace_string)
      # remove spaces inserted due to padding.
      line = line.replace(" ", "")
      # restore actual spaces.
      line = line.replace(replace_string, " ")

      # translate special characters
      line = line.replace("\\n", "\n")
      line = line.replace("\\r", "\r")
      line = line.replace("\\t", "\t")
      line = line.replace("\\0", "\0")
      
      # remove new line character at the end of the line
      if len(message+line) != msglen and line.endswith("\n"):
        line = line[:-1]

      message += line

    #if len(message) != msglen:
    #  raise Exception("Unexpected format when reading message: " +
    #                   message)

  return '"' + message + '"'


def _get_stat(fh, result):
  """
  Returns a tuple (st_dev, st_ino, st_mode, st_nlink, st_uid, st_gid,
          st_blksize, st_blocks, st_size_or_rdev_value, st_atime,
          st_mtime, st_ctime)

  The stat structure is given in the lines following the current
  line. If the lines contain the information needed, the lines are
  read and the information returned in a tuple. If the line is not of
  the expected format an exception is raised.
  """
  # initialize expected values.
  st_dev = ""
  st_ino = ""
  st_mode = ""
  st_nlink = ""
  st_uid = ""
  st_gid = ""
  is_st_size = False
  st_size_or_rdev_value = ""
  st_atime = ""
  st_mtime = ""
  st_ctime = ""
  st_blksize = ""
  st_blocks = ""
  
  skip_rest = False
  # if the syscall returned an error, don't parse the stat structure
  if result[0] != -1:
    # first line contains st_dev, st_ino, st_mode, st_nlink, st_uid,
    # st_gid and st_size or st_rdev
    # Example format: 
    # 3201/2: d=0x049C0000 i=125824 m=002620 l=1 u=0 g=7 rdev=0x00600004
    # 3201/1: d=0x00780000 i=185862 m=010644 l=1 u=0 g=0 sz=56
    last_file_pos = fh.tell()
    line = fh.readline()
    if (line.find("d=") != -1 and line.find("i=") != -1 and
        line.find("m=") != -1 and line.find("l=") != -1 and 
        line.find("u=") != -1 and line.find("g=") != -1 and 
        (line.find("sz=") != -1 or line.find("rdev=") != -1)):
      # parse the values from the line
      st_dev = line[line.find("d=")+2:line.find("i=")].strip()
      st_ino = line[line.find("i=")+2:line.find("m=")].strip()
      st_mode = line[line.find("m=")+2:line.find("l=")].strip()
      st_nlink = line[line.find("l=")+2:line.find("u=")].strip()
      st_uid = line[line.find("u=")+2:line.find("g=")].strip()
      # parse either st_size or st_rdev
      if line.find("sz=") != -1:
        is_st_size = True
        st_gid = line[line.find("g=")+2:line.find("sz=")].strip()
        st_size_or_rdev_value = line[line.find("sz=")+3:].strip()
      else:
        st_gid = line[line.find("g=")+2:line.find("rdev=")].strip()
        st_size_or_rdev_value = line[line.find("rdev=")+5:].strip()
    else:
      # undo reading so that the next line will be read in the next
      # iteration.
      fh.seek(last_file_pos)
      # if the first stat line is missing then so will all the other
      # stat lines
      skip_rest = True

    
    if not skip_rest:
      # second line contains the st_atime
      # Example format
      # 3201/1:  at = Feb  8 01:44:59 EST 2013  [ 1360305899.475745000 ]
      line = fh.readline()
      if line.find("at =") != -1 and line.find("[") != -1:
        # parse the values from the line
        st_atime = line[line.find("at =")+4:line.find("[")].strip()
      else:
        raise Exception("Unexpected format when translating second line "
                        "of stat: " + line)
      # third line contains the st_mtime
      # Example format
      # 3201/1:  mt = Feb  7 13:38:48 EST 2013  [ 1360262328.015187000 ]
      line = fh.readline()
      if line.find("mt =") != -1 and line.find("[") != -1:
        # parse the values from the line
        st_mtime = line[line.find("mt =")+4:line.find("[")].strip()
      else:
        raise Exception("Unexpected format when translating third line "
                        "of stat: " + line)
      
      # forth line contains the st_ctime
      # Example format
      # 3201/1:  ct = Feb  7 13:38:48 EST 2013  [ 1360262328.373997000 ]
      line = fh.readline()
      if line.find("ct =") != -1 and line.find("[") != -1:
        # parse the values from the line
        st_ctime = line[line.find("ct =")+4:line.find("[")].strip()
      else:
        raise Exception("Unexpected format when translating forth line "
                        "of stat: " + line)
      
      # fifth line contains st_blksize and st_blocks
      # Example format: 
      # 3201/1:       bsz=8192  blks=2     fs=ufs
      line = fh.readline()
      if (line.find("bsz=") != -1 and line.find("blks=") != -1):
        # parse the values from the line
        st_blksize = line[line.find("bsz=")+4:line.find("blks=")].strip()
        st_blocks = line[line.find("blks=")+5:line.find("fs=")].strip()
        # we skip the file system type here.
      else:
        raise Exception("Unexpected format when translating fifth line "
                        "of stat: " + line)

  # translate to expected format.
  # Example expected format:
  # st_dev=makedev(8, 6)
  # st_ino=697814
  # st_mode=S_IFREG|0664
  # st_nlink=1
  # st_uid=1000
  # st_gid=1000
  # st_blksize=4096
  # st_blocks=0
  # st_size=0 or st_rdev=makedev(136, 5)
  # st_atime=2013/03/06-00:17:54
  # st_mtime=2013/03/06-00:17:54
  # st_ctime=2013/03/06-00:17:54
  st_dev = "st_dev=" + st_dev
  st_ino = "st_ino=" + st_ino
  
  if st_mode.isdigit():
    st_mode = _translate_mode(st_mode)
  
  st_mode = "st_mode=" + st_mode
  st_nlink = "st_nlink=" + st_nlink
  st_uid = "st_uid=" + st_uid
  st_gid = "st_gid=" + st_gid
  st_blksize = "st_blksize=" + st_blksize
  st_blocks = "st_blocks=" + st_blocks
  
  if is_st_size:
    st_size_or_rdev_value = "st_size=" + st_size_or_rdev_value
  else:
    st_size_or_rdev_value = "st_rdev=" + st_size_or_rdev_value
  
  if len(st_atime.split()) == 5:
    st_atime = _translate_time(st_atime)
  st_atime = "st_atime=" + st_atime

  if len(st_mtime.split()) == 5:
    st_mtime = _translate_time(st_mtime)
  st_mtime = "st_mtime=" + st_mtime
  
  if len(st_ctime.split()) == 5:
    st_ctime = _translate_time(st_ctime)
  st_ctime = "st_ctime=" + st_ctime + "}"

  return (st_dev, st_ino, st_mode, st_nlink, st_uid, st_gid,
          st_blksize, st_blocks, st_size_or_rdev_value, st_atime,
          st_mtime, st_ctime)


def _get_statvfs(fh, result):
  """
  Returns a tuple (f_type, f_bsize, f_blocks, f_bfree, f_bavail, f_files, 
                   f_ffree, f_fsid, f_namelen, f_frsize)

  The statvfs structure is given in the lines following the current line. If the 
  lines contain the information needed, the lines are read and the information 
  returned in a tuple. If the line is not of the expected format an exception is 
  raised.
  """

  # initialize expected values.
  f_type = ""
  f_bsize = ""
  f_blocks = ""
  f_bfree = ""
  f_bavail = ""
  f_files = ""
  f_ffree = ""
  f_fsid = ""
  f_namelen = ""
  f_frsize = ""
  
  skip_rest = False
  # if the syscall returned an error, don't parse the statvfs structure
  if result[0] != -1:
    # first line:
    # 2373:   bsize=8192       frsize=1024      blocks=8139687  bfree=3830956  
    last_file_pos = fh.tell()
    line = fh.readline()
    
    if (line.find("bsize=") != -1 and line.find("frsize=") != -1 and
        line.find("blocks=") != -1 and line.find("bfree=") != -1):
      # parse the values from the line
      f_bsize = line[line.find("bsize=")+6:line.find("frsize=")].strip()
      f_frsize = line[line.find("frsize=")+7:line.find("blocks=")].strip()
      f_blocks = line[line.find("blocks=")+7:line.find("bfree=")].strip()
      f_bfree = line[line.find("bfree=")+6:].strip()
    else:
      # undo reading so that the next line will be read in the next
      # iteration.
      fh.seek(last_file_pos)
      # if the first statvfs line is missing then so will all the other
      # statvfs lines
      skip_rest = True

    if not skip_rest:
      # second line:
      # 2373:   bavail=3749560   files=984256     ffree=797256    favail=797256   
      line = fh.readline()
      if (line.find("bavail=") != -1 and line.find("files=") != -1 and 
          line.find("ffree=") != -1 and line.find("favail=") != -1):
        # parse the values from the line
        f_bavail = line[line.find("bavail=")+7:line.find("files=")].strip()
        f_files = line[line.find("files=")+6:line.find("ffree=")].strip()
        f_ffree = line[line.find("ffree=")+6:line.find("favail=")].strip()
      else:
        raise Exception("Unexpected format when translating second line "
                        "of statvfs: " + line)

    if not skip_rest:
      # third line:
      # 2373:   fsid=0x780000    basetype=ufs     namemax=255
      line = fh.readline()
      if (line.find("fsid=") != -1 and line.find("basetype=") != -1 and 
          line.find("namemax=") != -1):
        # parse the values from the line
        f_fsid = line[line.find("fsid=")+5:line.find("basetype=")].strip()
        f_type = line[line.find("basetype=")+9:line.find("namemax=")].strip()
        f_namelen = line[line.find("namemax=")+8:].strip()
      else:
        raise Exception("Unexpected format when translating third line "
                        "of statvfs: " + line)
      

  # translate to expected format.
  # Example expected format:
  # 7196  fstatfs(3, {f_type="EXT2_SUPER_MAGIC", f_bsize=4096, 
  #                   f_blocks=4553183, f_bfree=1919236, f_bavail=1687940, 
  #                   f_files=1158720, f_ffree=658797, 
  #                   f_fsid={-1853641883, -1823071587}, 
  #                   f_namelen=255, f_frsize=4096}) = 0
  f_type = "f_type=" + f_type
  f_bsize = "f_bsize=" + f_bsize
  f_blocks = "f_blocks=" + f_blocks
  f_bfree = "f_bfree=" + f_bfree
  f_bavail = "f_bavail=" + f_bavail
  f_files = "f_files=" + f_files
  f_ffree = "f_ffree=" + f_ffree
  f_fsid = "f_fsid=" + f_fsid
  f_namelen = "f_namelen=" + f_namelen
  f_frsize = "f_frsize=" + f_frsize + "}"
  
  return (f_type, f_bsize, f_blocks, f_bfree, f_bavail, f_files, f_ffree, f_fsid, 
          f_namelen, f_frsize)


def _translate_mode(mode):
  """
  Translate mode from format:
  100755 to "S_IFREG|0755"
  or
  040755 to "S_IFDIR|0755"
  """
  stat_flags = {
    160000:"S_IFPORT",
    150000:"S_IFDOOR",
    140000:"S_IFSOCK",
    120000:"S_IFLNK",
    100000:"S_IFREG",
    60000:"S_IFBLK",
    60000:"S_IFBLK",
    50000:"S_IFNAME",
    40000:"S_IFDIR",
    20000:"S_IFCHR",
    10000:"S_IFIFO",
    4000:"S_ISUID",
    2000:"S_ISGID",
    1000:"S_ISVTX"
  }
  
  mode = int(mode)
  # separate flag bits and mode bits
  flag_num = mode - mode % 1000
  mode = mode % 1000

  flags = ""
  while flag_num != 0:
    for f in sorted(stat_flags.keys(), reverse=True):
      if flag_num >= f:
        if flags == "":
          flags = stat_flags[f]
        else:
          flags += "|" + stat_flags[f]

        flag_num -= f
        break
  
  if mode != 0:
    flags += "|0" + str(mode)

  return flags


def _translate_fcntl(num):
  """
  Translate fcntl return value from format:
  2 to "O_RDWR"
  or
  130 to "O_NONBLOCK|O_RDWR"
  """

  # taken from Solaris 10: /usr/include/sys/fcntl.h
  fcntl_flags = {
    0:"O_RDONLY",
    1:"O_WRONLY",
    2:"O_RDWR",
    4:"O_NDELAY",
    8:"O_APPEND",
    16:"O_SYNC",
    64:"O_DSYNC",
    128:"O_NONBLOCK",
    4096:"O_PRIV",
    8192:"O_LARGEFILE",
    32768:"O_RSYNC"
  }
  
  num = int(num)

  flags = ""
  while num != 0:
    if DEBUG:
      print num
    for f in sorted(fcntl_flags.keys(), reverse=True):
      if num >= f:
        if flags == "":
          flags = fcntl_flags[f]
        else:
          flags += "|" + fcntl_flags[f]

        num -= f
        break

  if flags == "":
    return "O_RDONLY"
  return flags


def _translate_time(time):
  """
  Translate time from format:
  Feb  8 01:44:59 EST 2013
  to format:
  2013/03/06-00:17:54
  """
  # get all parts
  time_parts = time.split()
  # do we have the correct number of parts?
  if len(time_parts) != 5:
    raise Exception("Unexpected number of parts in time: " + time)
  # validate month
  months = {"Jan":"01", "Feb":"02", "Mar":"03", "Apr": "04", 
            "May":"05", "Jun":"06", "Jul":"07", "Aug":"08", 
            "Sep":"09", "Oct":"10", "Nov":"11", "Dec":"12"}
  if time_parts[0] in months:
    time_parts[0] = months.get(time_parts[0])
  else:
    raise Exception("Unexpected format when translating month " + 
                    time_parts[0] + " of time: " + time)
  # time_parts[1] should be a number representing the day.
  try:
    int(time_parts[1])
  except ValueError:
    raise Exception("Unexpected format when translating day " + 
                    time_parts[1] + " of time: " + time)
  else:
    # if day is less than 10 prepend a 0.
    if int(time_parts[1]) < 10:
      time_parts[1] = "0" + time_parts[1]
  # validate hour:minute:second
  hour_minute_second = time_parts[2].split(":")
  if (len(hour_minute_second) != 3 or not 
      hour_minute_second[0].isdigit() or not
      hour_minute_second[1].isdigit() or not
      hour_minute_second[2].isdigit()):
    raise Exception("Unexpected format when translating "
                    "hour:minute:second " + time_parts[2] + 
                    " of time: " + time)
  # time_parts[4] should be a number representing the year.
  try:
    int(time_parts[4])
  except ValueError:
    raise Exception("Unexpected format when translating year " + 
                    time_parts[4] + " of time: " + time)
  return (time_parts[4] + "/" + time_parts[0] + "/" + time_parts[1] +
         "-" + time_parts[2])
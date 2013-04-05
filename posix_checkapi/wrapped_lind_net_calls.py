"""
  Author: Justin Cappos
  Module: Network calls for Lind.   This is essentially POSIX written in
          Repy V2.   

  Start Date: January 14th, 2012

  My goal is to write a simple and relatively accurate implementation of POSIX
  in Repy V2.   This module contains most of the network calls.   A lind
  client can execute those calls and they will be mapped into my Repy V2 
  code where I will more or less faithfully execute them.   Since Repy V2
  does not support some of the socket options, I will fake (or ignore) these.
  There will also be a few minor parts of the implementation that might 
  need to interact with the file system portion of the API.   This will be 
  for things like getting file descriptors / socket descriptors.
  For Unix domain sockets, etc. we'll use loopback sockets.

  Much like the fs API, rather than do all of the struct packing, etc. here, I 
  will do it elsewhere.  This will allow me to test this in Python / Repy
  without unpacking / repacking.

"""


dy_import_module_symbols("lind_fs_constants")
dy_import_module_symbols("lind_net_constants")
dy_import_module_symbols("wrapped_lind_fs_calls")
dy_import_module_symbols("fs_net_handler")

#from lind_fs_constants import *
#from lind_net_constants import *
#from wrapped_lind_fs_calls import *
#import wrapped_lind_fs_calls as lind_fs_calls

# If we do not know the ip address of something we need to temporarily store 
# this as the address.
UNKNOWN_IP = "2.2.2.2"



# Since Repy does not have a concept of descriptors or binding before 
# connecting, we will fake all of this.   I will determine the usable ports
# and then choose from them when it's unspecified.


# I'm not overly concerned about efficiency right now.   I'm more worried
# about correctness.   As a result, I'm not going to optimize anything yet.
#

# I'll keep a little metadata for each socket descriptor (in the file
# descriptor table).   It will look like this:
# {'domain': AF_INET, 'type': SOCK_STREAM, 'protocol': IPPROTO_TCP, 
#  'localip': '1.2.3.4', 'localport':12345, 'remoteip': '5.6.7.8', 
#  'remoteport':6789, 'socketobjectid':5, 'mode':S_IFSOCK | 0666, 'options':0,
#  'sndbuf':131070, 'rcvbuf': 262140, 'state':NOTCONNECTED}
#
# To make dup and dup2 work correctly, I'll keep a socketobjecttable instead
# of including them in the filedescriptortable...
#



# States for my own internal use:

NOTCONNECTED = 128
CONNECTED = 256
LISTEN = 512

# contains open file descriptor information... (keyed by fd)
# filedescriptortable = {}

# contains socket objects... (keyed by id)   Mostly done for dup / dup2
socketobjecttable = {}

# This is raised to return an error...   It's the same as for the file 
# system calls
class SyscallError(Exception):
  """A system call had an error"""


# This is raised if part of a call is not implemented
class UnimplementedError(Exception):
  """A call was called with arguments that are not fully implemented"""

# This is raised if the call's argument contain a fd that is ignored
class IgnoredFileDescriptorWarning(Warning):
  """A call was called with a file descriptors that is ignored"""


######################   Generic Helper functions   #########################


# a list of udp ports already used.   This is used to help us figure out a good
# available port
usedudpportsset = set([])
# these are the ports we possibly could use...
usableudpportsset = getresources()[0]['messport'].copy()

# the same for tcp...
usedtcpportsset = set([])
usabletcpportsset = getresources()[0]['connport'].copy()


# We need a helper that gets an available port...
# Get the first unused port and return it...
def _get_available_udp_port():
  for port in usableudpportsset:
    if port not in usedudpportsset:
      return port
  
  # this is probably the closest syscall.   No buffer space available...
  raise SyscallError("_get_available_udp_port","ENOBUFS","No UDP port available")



# A verbatim copy of the above...   It's so simple, I guess it's okay to do so
def _get_available_tcp_port():
  for port in usabletcpportsset:
    if port not in usedtcpportsset:
      return port
  
  # this is probably the closest syscall.   No buffer space available...
  raise SyscallError("_get_available_tcp_port","ENOBUFS","No TCP port available")



STARTINGSOCKOBJID = 0
MAXSOCKOBJID = 1024

# get an available socket object ID...
def _get_next_socketobjid():
  for sockobjid in range(STARTINGSOCKOBJID,MAXSOCKOBJID):
    if not sockobjid in socketobjecttable:
      return sockobjid

  raise SyscallError("_get_next_socketobjid","ENOBUFS","Insufficient buffer space is available to create a new socketobjid")

def _insert_into_socketobjecttable(socketobj):
  nextentry = _get_next_socketobjid()
  socketobjecttable[nextentry] = socketobj
  return nextentry



#################### The actual system calls...   #############################



##### SOCKET  #####


# A private helper that initializes a socket given validated arguments.
def _socket_initializer(domain,socktype,protocol, blocking=False, cloexec=False):
  # get a file descriptor
  flags = []
  if blocking:
    flags.append('O_NONBLOCK')
  if cloexec:
    flags.append('O_CLOEXEC')

  newfd = get_next_fd()

  # NOTE: I'm intentionally omitting the 'inode' field.  This will make most
  # of the calls I did not change break.
  filedescriptortable[newfd] = {
      #'mode':S_IFSOCK|0666, # set rw-rw-rw- perms too. This is what POSIX does.
      'mode': ['S_IFSOCK', 'S_IRUSR', 'S_IWUSR', 'S_IRGRP', 'S_IWGRP', 'S_IROTH', 'S_IWOTH'],
      'domain':domain,
      'type':socktype,      # I'm using this name because it's used by POSIX.
      'protocol':protocol,
      # BUG: I may need to handle the global setting of options here...
      'options':[],          # start with all options off...
      'sndbuf':131070,      # buffersize (only used by getsockopt)
      'rcvbuf':262140,      # buffersize (only used by getsockopt)
      'state':NOTCONNECTED, # we start without any connection
      'lock':createlock(),
      'flags':flags,
      'errno':0
# We don't set the ip / ports or socketobjectid because they are unknown now.
  }

  return newfd
      


# int socket(int domain, int type, int protocol);
def socket_syscall(domain, socktype, protocol):
  """ 
    http://linux.die.net/man/2/socket
  """
  # this code is basically one huge case statement by domain

  domain = flag2list(domain)
  socktype = flag2list(socktype)
  protocol = flag2list(protocol)


  blocking = int('SOCK_NONBLOCK' in socktype) # check the non-blocking flag
  cloexec = int('SOCK_CLOEXEC' in socktype) # check the cloexec flag

  if blocking:
    print "Warning@socket_syscall: trying to create a non-blocking socket - we don't support that yet."

  # okay, let's do different things depending on the domain...
  if 'PF_INET' in domain :

    
    if 'SOCK_STREAM' in socktype:
      # If is 0, set to default (IPPROTO_TCP)
      if protocol == ['IPPROTO_IP']:
        protocol = ['IPPROTO_TCP']


      if 'IPPROTO_TCP' not in protocol :

        # add the returned fd to the ignore_fd list
        impl_ret, impl_errno = mycontext['posix_oracle'].pop()

        if impl_ret != -1:
          ignore_fd.append(impl_ret) 

        raise UnimplementedError("The only SOCK_STREAM implemented is TCP.  Unknown protocol:"+str(protocol))
      
      return _socket_initializer(domain,socktype,protocol,blocking, cloexec)


    # datagram!
    elif 'SOCK_DGRAM' in socktype:
      # If is 0, set to default (IPPROTO_UDP)
      if protocol == ['IPPROTO_IP']:
        protocol = ['IPPROTO_UDP']

      if 'IPPROTO_UDP' not in protocol:

        # add the returned fd to the ignore_fd list
        impl_ret, impl_errno = mycontext['posix_oracle'].pop()

        if impl_ret != -1:
          ignore_fd.append(impl_ret) 

        raise UnimplementedError("The only SOCK_DGRAM implemented is UDP.  Unknown protocol:"+str(protocol))
    
      return _socket_initializer(domain,socktype,protocol)
    else:
      # add the returned fd to the ignore_fd list
      impl_ret, impl_errno = mycontext['posix_oracle'].pop()

      if impl_ret != -1:
        ignore_fd.append(impl_ret) 

      raise UnimplementedError("Unimplemented sockettype: "+str(socktype))

  else:
    # add the returned fd to the ignore_fd list
    impl_ret, impl_errno = mycontext['posix_oracle'].pop()

    if impl_ret != -1:
      ignore_fd.append(impl_ret) 

    raise UnimplementedError("Unimplemented domain: "+str(domain))




##### BIND  #####

# the domain and addrlen are not used
def bind_syscall(fd, domain, localport, localip, addrlen):
  """ 
    http://linux.die.net/man/2/bind
  """
  if fd in ignore_fd:
    return IgnoredFileDescriptorWarning("bind_syscall", "The file descriptor is ignored.") 

  if fd not in filedescriptortable:
    raise SyscallError("bind_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("bind_syscall","ENOTSOCK","The descriptor is not a socket.")

  # Am I already bound?
  if 'localip' in filedescriptortable[fd]:
    raise SyscallError('bind_syscall','EINVAL',"The socket is already bound to an address")


  # Is someone else already bound to this address?
  for otherfd in filedescriptortable:
    # skip ours
    if fd == otherfd:
      continue

    # if not a socket, skip it...
    if 'domain' not in filedescriptortable[otherfd]:
      continue

    # if the protocol / domain/ type differ, ignore
    if filedescriptortable[otherfd]['domain'] != filedescriptortable[fd]['domain'] or filedescriptortable[otherfd]['type'] != filedescriptortable[fd]['type'] or filedescriptortable[otherfd]['protocol'] != filedescriptortable[fd]['protocol']:
      continue

    # if they are already bound to this address / port
    if 'localip' in filedescriptortable[otherfd] and filedescriptortable[otherfd]['localip'] == localip and filedescriptortable[otherfd]['localport'] == localport:
      # is SO_REUSEPORT in effect on both? I think everyone has to set 
      # SO_REUSEPORT (at least this is true on some OSes.   It's OS dependent)
      if 'SO_REUSEPORT' in filedescriptortable[fd]['options'] and 'SO_REUSEPORT' in filedescriptortable[otherfd]['options']:
        # all is well, continue...
        pass
      else:
        raise SyscallError('bind_syscall','EADDRINUSE',"Another socket is already bound to this address")

  # BUG (?): hmm, how should I support multiple interfaces?   I could either 
  # force them to pick the result of getmyip here or could return a different 
  # error later....   I think I'll wait.


  # If this is a UDP interface, then we should listen for udp datagrams
  # (there is no 'listen' so the time to start now)...
  if 'IPPROTO_UDP' in filedescriptortable[fd]['protocol']:
    if 'socketobjectid' in filedescriptortable[fd]:
      # BUG: I need to avoid leaking sockets, so I should close the previous...
      raise UnimplementedError("I should close the previous UDP listener when re-binding")
    oracle_setter('', None)
    udpsockobj = model_listenformessage('MainThread', localip, localport)
    filedescriptortable[fd]['socketobjectid'] = _insert_into_socketobjecttable(udpsockobj)
    
  

  # Done!   Let's set the information and bind later since Repy V2 doesn't 
  # support a separate call for binding...
  filedescriptortable[fd]['localip']=localip
  filedescriptortable[fd]['localport']=localport


  return 0






# int connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen);


##### CONNECT  #####

# domain and addrlen are not used
def connect_syscall(fd, domain, remoteport, remoteip, addrlen):
  """ 
    http://linux.die.net/man/2/connect
  """

  # Specify all non-deterministic errors that could occur.
  connect_nondeter_errors = ['ENETUNREACH', 'ENETUNREACH', 'ETIMEOUT', 'EADDRINUSE', 
                             'ECONNREFUSED', 'EINPROGRESS']

  if fd in ignore_fd:
    return IgnoredFileDescriptorWarning("connect_syscall", "The file descriptor is ignored.") 

  if fd not in filedescriptortable:
    raise SyscallError("connect_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("connect_syscall","ENOTSOCK","The descriptor is not a socket.")

  # includes CONNECTED and LISTEN
  if filedescriptortable[fd]['state'] != NOTCONNECTED:
    raise SyscallError("connect_syscall","EISCONN","The descriptor is already connected.")

  # Check with impl behavior, was it non-deterministic??
  impl_ret, impl_errno = mycontext['posix_oracle'].pop()
  if impl_errno != None:
    if impl_errno in connect_nondeter_errors:
      raise SyscallError("connect_syscall", impl_errno, "Non-deterministic error")


  # What I do depends on the protocol...
  # If UDP, set the items and return
  if 'IPPROTO_UDP' in filedescriptortable[fd]['protocol']:
    filedescriptortable[fd]['remoteip'] = remoteip
    filedescriptortable[fd]['remoteport'] = remoteport
    return 0


  # it's TCP!
  elif 'IPPROTO_TCP' in filedescriptortable[fd]['protocol']:

    # Am I already bound?   If not, we'll need to get an ip / port
    if 'localip' not in filedescriptortable[fd]:
      oracle_setter(UNKNOWN_IP, None)
      localip = model_getmyip('MainThread')
      localport = _get_available_tcp_port()

    else:
      localip = filedescriptortable[fd]['localip']
      localport = filedescriptortable[fd]['localport']

    try:
      oracle_setter('', None)
      # BUG: The timeout it configurable, right?
      newsockobj = model_openconnection("MainThread", remoteip, int(remoteport), localip, int(localport), 10)
 
    except AddressBindingError, e: #ND
      raise SyscallError('connect_syscall','ENETUNREACH','Network was unreachable because of inability to access local port / IP')
    except InternetConnectivityError, e: #ND
      raise SyscallError('connect_syscall','ENETUNREACH','Network was unreachable because of inability to access local port / IP')
    except TimeoutError, e: #ND
      raise SyscallError('connect_syscall','ETIMEOUT','Connection timed out')
    except CleanupInProgressError, e: #ND #JR: added.
      raise SyscallError('connect_syscall', 'EADDRINUSE','Cleanup is in progress')
    except ConnectionRefusedError, e: #ND
      raise SyscallError('connect_syscall','ECONNREFUSED','Connection refused.')
    except DuplicateTupleError, e: # Deterministic
      raise SyscallError('connect_syscall','EADDRINUSE','Network address in use')
 
    # fill in the file descriptor table...
    filedescriptortable[fd]['socketobjectid'] = _insert_into_socketobjecttable(newsockobj)
    filedescriptortable[fd]['localip'] = localip
    filedescriptortable[fd]['localport'] = localport
    filedescriptortable[fd]['remoteip'] = remoteip
    filedescriptortable[fd]['remoteport'] = remoteport

    filedescriptortable[fd]['state'] = CONNECTED

    # change the state and return success
    return 0
    
  else:
    raise UnimplementedError("Unknown protocol in connect()")

    






# ssize_t sendto(int sockfd, const void *buf, size_t len, int flags, const struct sockaddr *dest_addr, socklen_t addrlen);

##### SENDTO  #####

# length, domain, addrlen are not used
def sendto_syscall(fd, message, length, flags, domain, remoteport, remoteip, addrlen):
  """ 
    http://linux.die.net/man/2/sendto
  """
  flags = flag2list(flags)

  # Specify all non-deterministic errors that could occur.
  sendto_nondeter_errors = ['ENETUNREACH']

  if fd in ignore_fd:
    return IgnoredFileDescriptorWarning("sendto_syscall", "The file descriptor is ignored.") 

  if fd not in filedescriptortable:
    raise SyscallError("sendto_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("sendto_syscall","ENOTSOCK","The descriptor is not a socket.")

  if flags != []:
    raise UnimplementedError("Flags are not understood by sendto!")


  # Check with impl behavior, was it non-deterministic??
  impl_ret, impl_errno = mycontext['posix_oracle'].pop()
  if impl_errno != None:
    if impl_errno in sendto_nondeter_errors:
      raise SyscallError("connect_syscall", impl_errno, "Non-deterministic error")

  # if there is no IP / port, call send instead.   It will assume the other
  # end is connected...
  if remoteip == '' and remoteport == 0:
    mycontext['posix_oracle'].append((impl_ret,impl_errno))
    return send_syscall(fd,message,flags)

  if filedescriptortable[fd]['state'] == CONNECTED or filedescriptortable[fd]['state'] == LISTEN:
    raise SyscallError("sendto_syscall","EISCONN","The descriptor is connected.")


  if 'IPPROTO_TCP' in filedescriptortable[fd]['protocol']:
    raise SyscallError("sendto_syscall","EISCONN","The descriptor is connection-oriented.")
    
  # What I do depends on the protocol...
  # If UDP, set the items and return
  if 'IPPROTO_UDP' in filedescriptortable[fd]['protocol']:

    # If unspecified, use a new local port / the local ip
    if 'localip' not in filedescriptortable[fd]:
      oracle_setter(UNKNOWN_IP, None)
      localip = model_getmyip('MainThread')
      # EG: _get_available_tcp_port returns float ports! why? for now let's cast it
      localport = int(_get_available_tcp_port())
    else:
      localip = filedescriptortable[fd]['localip']
      localport = filedescriptortable[fd]['localport']

    try:
      # BUG: The timeout it configurable, right?
      oracle_setter(impl_ret, None)
      # EG: changed sendmessage to model_sendmessage
      #bytessent = sendmessage(remoteip, remoteport, message, localip, localport)
      bytessent = model_sendmessage('MainThread', remoteip, remoteport, message, localip, localport)


    except AddressBindingError, e:
      raise SyscallError('connect_syscall','ENETUNREACH','Network was unreachable because of inability to access local port / IP')
    except DuplicateTupleError, e:
      raise SyscallError('connect_syscall','EADDRINUSE','Network address in use')
 
    # fill in the file descriptor table...
    filedescriptortable[fd]['localip'] = localip
    filedescriptortable[fd]['localport'] = localport


    # return the characters sent!
    return bytessent

  else:
    raise UnimplementedError("Unknown protocol in sendto()")








# ssize_t send(int sockfd, const void *buf, size_t len, int flags);

##### SEND  #####

# msg_len is not used
def send_syscall(fd, message, msg_len, flags):
  """ 
    http://linux.die.net/man/2/send
  """
  # TODO: Change write() to call send when on a socket!!!

  # Nondeterministic errors that could occur with this call.
  send_nondeter_errors = ["EWOULDBLOCK","EPIPE","EBADF","EBADR","ENOLINK","EBADFD",
                          "ENETRESET","ECONNRESET","WSAEBADF","WSAENOTSOCK",
                          "WSAECONNRESET","EAGAIN"]
  flags = flag2list(flags)

  if fd in ignore_fd:
    return IgnoredFileDescriptorWarning("send_syscall", "The file descriptor is ignored.") 

  if fd not in filedescriptortable:
    raise SyscallError("send_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("send_syscall","ENOTSOCK","The descriptor is not a socket.")

  if flags != [] and 'MSG_NOSIGNAL' not in flags:
    raise UnimplementedError("Flags are not understood by send!")

  # includes NOTCONNECTED and LISTEN
  if 'IPPROTO_TCP' in filedescriptortable[fd]['protocol'] and filedescriptortable[fd]['state'] != CONNECTED:
    raise SyscallError("send_syscall","ENOTCONN","The descriptor is not connected.")


  if 'IPPROTO_TCP' not in filedescriptortable[fd]['protocol'] and 'IPPROTO_UDP' not in filedescriptortable[fd]['protocol']:
    raise SyscallError("send_syscall","EOPNOTSUPP","send not supported on this protocol.")
    
  # Check with impl behavior, was it non-deterministic??
  impl_ret, impl_errno = mycontext['posix_oracle'].pop()
  if impl_errno != None:
    assert impl_errno in send_nondeter_errors, "errno " +str(impl_errno)+ ", is unknown!"
    raise SyscallError("send_syscall", impl_errno, "Non-deterministic error")

  # I'll check this anyways, because I later might have multiple protos 
  # supported
  if 'IPPROTO_TCP' in filedescriptortable[fd]['protocol']:

    # get the socket so I can send...
    sockobj = socketobjecttable[filedescriptortable[fd]['socketobjectid']]
    
    # retry until it does not block...
    while True:
      try:
        oracle_setter(impl_ret, None)
        bytessent = model_socket_send('MainThread', sockobj, message)
        #bytessent = sockobj.send('MainThread', objid, message)
        break

      except Exception, e:
        # I think this shouldn't happen.   A closed socket should go to
        # NOTCONNECTED state.   This is an internal error...
        raise 
    
      # sleep and retry
      except SocketWouldBlockError, e:
        raise Exception("MODEL ERROR: I dont think this should happen.")
        sleep(RETRYWAITAMOUNT)
 

    # return the characters sent!
    return bytessent

  else:
    raise UnimplementedError("Unknown protocol in send()")

    

    





# ssize_t recvfrom(int sockfd, void *buf, size_t len, int flags, struct sockaddr *src_addr, socklen_t *addrlen);


##### RECVFROM  #####


# Wait this long between recv calls...
RETRYWAITAMOUNT = .001

# EG: TODO I'm not sure how this works.. need to check it out!
# Note that this call may be used by recv_syscall since they are so similar
def recvfrom_syscall(fd, buf_len, flags):
  """ 
    http://linux.die.net/man/2/recvfrom
  """
  flags = flag2list(flags)

  if fd in ignore_fd:
    return IgnoredFileDescriptorWarning("recvfrom_syscall", "The file descriptor is ignored.") 

  if fd not in filedescriptortable:
    raise SyscallError("recvfrom_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("recvfrom_syscall","ENOTSOCK","The descriptor is not a socket.")

  # Most of these are uninteresting
  if flags != []:
    raise UnimplementedError("Flags are not understood by recvfrom!")

  length, impl_errno = mycontext['posix_oracle'].pop()

  message, domain, remoteport, remoteip, addrlen = impl_errno

  # if there is no IP / port, call recv instead.   It will assume the other
  # end is connected...
  if remoteip == '' and remoteport == 0:
    return recv_syscall(fd,length,flags)


  # What I do depends on the protocol...
  if 'IPPROTO_TCP' in filedescriptortable[fd]['protocol']:

    # includes NOTCONNECTED and LISTEN
    if filedescriptortable[fd]['state'] != CONNECTED:
      raise SyscallError("recvfrom_syscall","ENOTCONN","The descriptor is not connected.")
    
    # I'm ready to recv, get the socket object...
    sockobj = socketobjecttable[filedescriptortable[fd]['socketobjectid']]

    remoteip = filedescriptortable[fd]['remoteip']
    remoteport = filedescriptortable[fd]['remoteport']

    # keep trying to get something until it works (or EOF)...
    while True:
      try:
        return remoteip, remoteport, model_socket_recv('MainThread', sockobj, length)

      except SocketClosedRemote, e:
        return remoteip, remoteport, ''

      # sleep and retry!
      # If O_NONBLOCK was set, we should re-raise this here...
      except SocketWouldBlockError, e:
        sleep(RETRYWAITAMOUNT)



  # If UDP, recieve a message and return...
  elif 'IPPROTO_UDP' in filedescriptortable[fd]['protocol']:

    # BUG / HELP!!!: Calling this with UDP and without binding does something I
    # don't really understand...   It seems to block but I don't know what is 
    # happening.   The socket isn't bound to a valid inode,etc from what I see.
    if 'localip' not in filedescriptortable[fd]:
      raise UnimplementedError("BUG / FIXME: Should bind before using UDP to recv / recvfrom")


    # get the udpsocket object...
    udpsockobj = socketobjecttable[filedescriptortable[fd]['socketobjectid']]

    # keep trying to get something until it works in most cases...
    while True:
      try:
        return model_udpserver_getmessage('MainThread', udpsockobj)

      # sleep and retry!
      # If O_NONBLOCK was set, we should re-raise this here...
      except SocketWouldBlockError, e:
        sleep(RETRYWAITAMOUNT)



  else:
    raise UnimplementedError("Unknown protocol in recvfrom()")









# ssize_t recv(int sockfd, void *buf, size_t len, int flags);

##### RECV  #####


def recv_syscall(fd, length, flags):
  """ 
    http://linux.die.net/man/2/recv
  """
  flags = flag2list(flags)

  if fd in ignore_fd:
    return IgnoredFileDescriptorWarning("recvfrom_syscall", "The file descriptor is ignored.") 

  # TODO: Change read() to call recv when on a socket!!!

  remoteip, remoteport, message = recvfrom_syscall(fd, length, flags)

  # we don't need the remoteip or remoteport for this...
  return message

    






# int getsockname(int sockfd, struct sockaddr *addrsocklen_t *" addrlen);


##### GETSOCKNAME  #####


def getsockname_syscall(fd):
  """ 
    http://linux.die.net/man/2/getsockname
  """

  if fd in ignore_fd:
    return IgnoredFileDescriptorWarning("getsockname_syscall", "The file descriptor is ignored.") 

  if fd not in filedescriptortable:
    raise SyscallError("getsockname_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("getsockname_syscall","ENOTSOCK","The descriptor is not a socket.")

  # if we know this, return it...
  if 'localip' in filedescriptortable[fd]:
    # JR: Model specific, since we now know what the IP should have been we can store it.
    if filedescriptortable[fd]['localip'] == UNKNOWN_IP:
      impl_ret, impl_errno = mycontext['posix_oracle'].pop()
      localip, localport = impl_ret
      oracle_setter(localip, impl_errno)
      localip = model_getmyip('MainThread')
      filedescriptortable[fd]['localip'] = localip
      filedescriptortable[fd]['localport'] = localport
     
    # EG: handle cases of OS-assigned random ports
    # This is usually happens when socket is bound to port 0
    if  filedescriptortable[fd]['localport'] == 0:
      impl_ret, impl_errno = mycontext['posix_oracle'].pop()
      impl_ip, impl_port = impl_ret
      if impl_ip == filedescriptortable[fd]['localip']:
      	filedescriptortable[fd]['localport'] = impl_port

    return filedescriptortable[fd]['localport'], filedescriptortable[fd]['localip'] 
  # EG: what if socket is not bound? 
  #else:
  #  impl_ret, impl_errno = mycontext['posix_oracle'].pop()
  #  localip, localport = impl_ret
  #  oracle_setter(localip, impl_errno)
  #  localip = model_getmyip('MainThread')
  #  filedescriptortable[fd]['localip'] = localip
  #  filedescriptortable[fd]['localport'] = localport
 
  #  return filedescriptortable[fd]['localip'], filedescriptortable[fd]['localport']
    
  # otherwise, return '0.0.0.0', 0
  else:  
    return 0, '0.0.0.0'
  

    


    




##### GETPEERNAME  #####


def getpeername_syscall(fd):
  """ 
    http://linux.die.net/man/2/getpeername
  """
  if fd in ignore_fd:
    return IgnoredFileDescriptorWarning("getpeername_syscall", "The file descriptor is ignored.") 

  if fd not in filedescriptortable:
    raise SyscallError("getpeername_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("getpeername_syscall","ENOTSOCK","The descriptor is not a socket.")


  # if we don't know this, we should raise an exception
  if 'remoteip' not in filedescriptortable[fd]:
    raise SyscallError("getpeername_syscall","ENOTCONN","The descriptor is not connected.")

  # if we know this, return it...
  return filedescriptortable[fd]['remoteport'], filedescriptortable[fd]['remoteip']
  
  





# int listen(int sockfd, int backlog);



##### LISTEN  #####


# I ignore the backlog
def listen_syscall(fd,backlog):
  """ 
    http://linux.die.net/man/2/listen
  """
  backlog = flag2list(backlog)

  if fd in ignore_fd:
    return IgnoredFileDescriptorWarning("listen_syscall", "The file descriptor is ignored.") 

  if fd not in filedescriptortable:
    raise SyscallError("listen_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("listen_syscall","ENOTSOCK","The descriptor is not a socket.")

  # BUG: I need to check if someone else is already listening here...

  

  # If UDP, raise an exception
  if 'IPPROTO_UDP' in filedescriptortable[fd]['protocol']:
    raise SyscallError("listen_syscall","EOPNOTSUPP","This protocol does not support listening.")

  # it's TCP!
  elif 'IPPROTO_TCP' in filedescriptortable[fd]['protocol']:

    if filedescriptortable[fd]['state'] == LISTEN:
      # already done!
      return 0

    if 'localip' not in filedescriptortable[fd]:
      # the real POSIX impl picks a random port and listens on 0.0.0.0.   
      # I think this is unnecessary to implement.
      raise UnimplementedError("listen without bind")

    # If it's connected, this is still allowed, but I won't implement it...
    if filedescriptortable[fd]['state'] == CONNECTED:
      # BUG: I would need to close this (if the last) to handle this right...
      raise UnimplementedError("Listen should close the existing connected socket")

    # Is someone else already listening on this address?   This may happen
    # with SO_REUSEPORT
    for otherfd in filedescriptortable:
      # skip ours
      if fd == otherfd:
        continue

      # if not a socket, skip it...
      if 'domain' not in filedescriptortable[otherfd]:
        continue

      # if they are not listening, skip it...
      if filedescriptortable[otherfd]['state'] != LISTEN:
        continue

      # if the protocol / domain/ type differ, ignore
      if filedescriptortable[otherfd]['domain'] != filedescriptortable[fd]['domain'] or filedescriptortable[otherfd]['type'] != filedescriptortable[fd]['type'] or filedescriptortable[otherfd]['protocol'] != filedescriptortable[fd]['protocol']:
        continue

      # if they are already bound to this address / port
      if filedescriptortable[otherfd]['localip'] == filedescriptortable[fd]['localip'] and filedescriptortable[otherfd]['localport'] == filedescriptortable[fd]['localport']:
        raise SyscallError('bind_syscall','EADDRINUSE',"Another socket is already bound to this address")


    # otherwise, all is well.   Let's set it up!
    filedescriptortable[fd]['state'] = LISTEN
    
    # BUG: I'll let anything go through for now.   I'm fairly sure there will 
    # be issues I may need to handle later.
    oracle_setter('', None)
    newsockobj = model_listenforconnection('MainThread', filedescriptortable[fd]['localip'], filedescriptortable[fd]['localport'])
    filedescriptortable[fd]['socketobjectid'] = _insert_into_socketobjecttable(newsockobj)

    # change the state and return success
    return 0

  else:
    raise UnimplementedError("Unknown protocol in listen()")

    








# int accept(int sockfd, struct sockaddr *addr, socklen_t *addrlen);




##### ACCEPT  #####


# returns ip, port, sockfd
def accept_syscall(fd):
  """ 
    http://linux.die.net/man/2/accept
  """
  if fd in ignore_fd:
    return IgnoredFileDescriptorWarning("accept_syscall", "The file descriptor is ignored.") 

  if fd not in filedescriptortable:
    raise SyscallError("accept_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("accept_syscall","ENOTSOCK","The descriptor is not a socket.")


  # If UDP, raise an exception
  if 'IPPROTO_UDP' in filedescriptortable[fd]['protocol']:
    raise SyscallError("accept_syscall","EOPNOTSUPP","This protocol does not support listening.")


  # it's TCP!
  elif 'IPPROTO_TCP' in filedescriptortable[fd]['protocol']:

    # must be listening
    if filedescriptortable[fd]['state'] != LISTEN:
      raise SyscallError("accept_syscall","EINVAL","Must call listen before accept.")

    listeningsocket = socketobjecttable[filedescriptortable[fd]['socketobjectid']]

    # now we should loop (block) until we get an incoming connection
    while True:
      try:
        sockfd, impl_errno = mycontext['posix_oracle'].pop() # real impl return.
        # domain and addrlen are not used
        domain, remoteport, remoteip, addrlen = impl_errno
        oracle_setter((remoteip, remoteport, str(sockfd)), None)
        remoteip, remoteport, acceptedsocket = model_tcpserver_getconnection('MainThread', listeningsocket)
        #remoteip, remoteport, acceptedsocket = listeningsocket.getconnection()

      # sleep and retry
      except SocketWouldBlockError, e:
        sleep(RETRYWAITAMOUNT)
      else:
        
        newfd = _socket_initializer(filedescriptortable[fd]['domain'],filedescriptortable[fd]['type'],filedescriptortable[fd]['protocol'])

        filedescriptortable[newfd]['state'] = CONNECTED
        filedescriptortable[newfd]['localip'] = filedescriptortable[fd]['localip']
        filedescriptortable[newfd]['localport'] = filedescriptortable[fd]['localport']
        filedescriptortable[newfd]['remoteip'] = remoteip
        filedescriptortable[newfd]['remoteport'] = remoteport
        filedescriptortable[newfd]['socketobjectid'] = _insert_into_socketobjecttable(acceptedsocket)

        return remoteip, remoteport, newfd

  else:
    raise UnimplementedError("Unknown protocol in accept()")

    






# int getsockopt(int sockfd, int level, int optname, void *optval, socklen_t *optlen);


# I'm just going to set these binary options or return the previous setting.   
# In most cases, this will be while doing nothing.
STOREDSOCKETOPTIONS = [ 'SO_LINGER', # ignored
                        'SO_KEEPALIVE', # ignored
                        'SO_SNDLOWAT', # ignored
                        'SO_RCVLOWAT', # ignored
                        'SO_REUSEPORT', # used to allow duplicate binds...
                      ]


##### GETSOCKOPT  #####
def getsockopt_syscall(fd, level, optname):
  """ 
    http://linux.die.net/man/2/getsockopt
  """
  level = flag2list(level)
  optname = flag2list(optname)

  if fd in ignore_fd:
    return IgnoredFileDescriptorWarning("getsockopt_syscall", "The file descriptor is ignored.") 

  if fd not in filedescriptortable:
    raise SyscallError("getsockopt_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("getsockopt_syscall","ENOTSOCK","The descriptor is not a socket.")

  # This should really be SOL_SOCKET, however, we'll also handle a few others
  if 'SOL_UDP' in level :
    raise UnimplementedError("UDP is not supported for getsockopt")

  # TCP...  Ignore most things...
  elif 'SOL_TCP' in level:
    # do nothing
    
    raise UnimplementedError("TCP options not remembered by getsockopt")



  elif 'SOL_SOCKET' in level:
    # this is where the work happens!!!
    if 'SO_ACCEPTCONN' in optname:
      # indicate if we are accepting connections...
      if filedescriptortable[fd]['state'] == LISTEN:
        return 1
      else:
        return 0

    # if the option is a stored binary option, just return it...
    if len(optname) == 1 and optname[0] in STOREDSOCKETOPTIONS:
      if optname in filedescriptortable[fd]['options']:
        return 1
      else:
        return 0

    # Okay, let's handle the (ignored) buffer settings...
    if 'SO_SNDBUF' in optname:
        return 1

    if 'SO_RCVBUF' in optname:
        return 1


    # similarly, let's handle the SNDLOWAT and RCVLOWAT, etc.
    # BUG?: On Mac, this seems to be stored much like the buffer settings
    if 'SO_SNDLOWAT' in optname or 'SO_RCVLOWAT' in optname:
      return 1


    # return the type if asked...
    if 'SO_TYPE' in optname:
      # EG:TODO don't know if this is the correct way to return the value
      if filedescriptortable[fd]['type'] is not None:
        return 1

    # I guess this is always true!?!?   I certainly don't handle it.
    # EG: I don't think it's always true... so, I'll change it
    if 'SO_OOBINLINE' in optname:
      if 'SO_OOBINLINE' in filedescriptortable[fd]['options']:
        return 1
      else:
        return 0

    raise UnimplementedError("Unknown option in getsockopt()")

  else:
    raise UnimplementedError("Unknown level in getsockopt()")








# int setsockopt(int sockfd, int level, int optname, const void *optval, socklen_t optlen);

# optlen not used
##### SETSOCKOPT  #####
def setsockopt_syscall(fd, level, optname, optval, optlen):
  """ 
    http://linux.die.net/man/2/setsockopt
  """
  level = flag2list(level)
  optname = flag2list(optname)
  optval = flag2list(optval)

  if fd in ignore_fd:
    return IgnoredFileDescriptorWarning("setsockopt_syscall", "The file descriptor is ignored.") 

  if fd not in filedescriptortable:
    raise SyscallError("setsockopt_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("setsockopt_syscall","ENOTSOCK","The descriptor is not a socket.")

  # This should really be SOL_SOCKET, however, we'll also handle a few others
  if 'SOL_UDP' in level:
    raise UnimplementedError("UDP is not supported for setsockopt")

  # TCP...  Ignore most things...
  elif 'SOL_TCP' in level:
    # do nothing
    if 'TCP_NODELAY' in optname:
      return 0
 
    # otherwise return an error
    raise UnimplementedError("TCP options not remembered by setsockopt")


  elif 'SOL_SOCKET' in level:
    # this is where the work happens!!!

    if 'SO_ACCEPTCONN' in optname or 'SO_TYPE' in optname or 'SO_SNDLOWAT' in optname or 'SO_RCVLOWAT' in optname:
      raise SyscallError("setsockopt_syscall","ENOPROTOOPT","Cannot set option using setsockopt.")

    # if the option is a stored binary option, just return it...
    if len(optname) == 1 and optname[0] in STOREDSOCKETOPTIONS:
      newoptions = filedescriptortable[fd]['options']

      # if the value is set, unset it...
      if len(optname) == 1 and optname[0] in newoptions:
        newoptions.remove(optname)
        return 1

      # now let's set this if we were told to
      if optval != []:
        # this value should be 1!!!   Nothing else is allowed
        assert(optval[0] == 1)
        newoptions.append(optname[0])

      filedescriptortable[fd]['options'] = newoptions
      return 0
      

    # Okay, let's handle the (ignored) buffer settings...
    if 'SO_SNDBUF' in optname:
      filedescriptortable[fd]['sndbuf'] = optval[0]
      return 0

    if 'SO_RCVBUF' in optname:
      filedescriptortable[fd]['rcvbuf'] = optval[0]
      return 0

    # I guess this is always true!?!?   I certainly don't handle it.
    if 'SO_OOBINLINE' in optname:
      # I can only handle this being true...
      assert(optval[0] == 1)
      return 0

    raise UnimplementedError("Unknown option in setsockopt()")

  else:
    raise UnimplementedError("Unknown level in setsockopt()")





# Helps to determine if the fd is a network or file system related, then 
# attempts to close it.
def close_network_fd(fd):
  # BUG: need to check for duplicate entries (ala dup / dup2)
  if 'socketobjectid' in filedescriptortable[fd]:
    thesocket = socketobjecttable[filedescriptortable[fd]['socketobjectid']]

    if 'IPPROTO_UDP' in filedescriptortable[fd]['protocol']:
      model_udpserver_close('MainThread', thesocket)
    elif 'IPPROTO_TCP' in filedescriptortable[fd]['protocol']:
      if filedescriptortable[fd]['state'] == LISTEN:
        model_tcpserver_close('MainThread', thesocket)
      else:
        model_socket_close('MainThread', thesocket)
    else:
      raise UnimplementedError("Unable to close non-udp/tcp sockets.")

    del socketobjecttable[filedescriptortable[fd]['socketobjectid']]
    del filedescriptortable[fd]['socketobjectid']
      
  filedescriptortable[fd]['state'] = NOTCONNECTED
  return 0



# int shutdown(int sockfd, int how);

##### SHUTDOWN  #####
def setshutdown_syscall(fd, how):
  """ 
    http://linux.die.net/man/2/shutdown
  """
  how = flag2list(how)

  if fd in ignore_fd:
    return IgnoredFileDescriptorWarning("setshutdown_syscall", "The file descriptor is ignored.") 

  if fd not in filedescriptortable:
    raise SyscallError("shutdown_syscall","EBADF","The file descriptor is invalid.")

  if not IS_SOCK(filedescriptortable[fd]['mode']):
    raise SyscallError("shutdown_syscall","ENOTSOCK","The descriptor is not a socket.")


  if 'SHUT_RD' in how or 'SHUT_WR' in how:

    raise UnimplementedError("Partial shutdown not implemented.")

  
  # let's shut this down...
  elif 'SHUT_RDWR' in how:
    # BUG: need to check for duplicate entries (ala dup / dup2)
    #if 'socketobjectid' in filedescriptortable[fd]:
    #  thesocket = socketobjecttable[filedescriptortable[fd]['socketobjectid']]
    #  thesocket.close()
    #  del socketobjecttable[filedescriptortable[fd]['socketobjectid']]
    #  del filedescriptortable[fd]['socketobjectid']
    #  
    #filedescriptortable[fd]['state'] = NOTCONNECTED
    #return 0
    return close_network_fd(fd)

  else:
    # BUG: I'm not exactly clear as to how to handle this...
    
    raise SyscallError("shutdown_syscall","EINVAL","Shutdown given an invalid how")



# int socketpair(int domain, int type, int protocol, int socket_vector[2]);
# ssize_t recvmsg(int sockfd, struct msghdr *msg, int flags);
# ssize_t sendmsg(int sockfd, const struct msghdr *msg, int flags);


def inet_ntoa(ipaddress):
  """
  Convert an IP address in integer form to a dot-and-number string

  This is 
  
  """
  a,b,c,d = struct_unpack("<B<B<B<B",ipaddress)
  return str(a) + "." + str(b) + "." +str(c) + "." +str(d)

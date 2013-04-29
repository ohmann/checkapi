#define _GNU_SOURCE
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <sys/syscall.h>
#include <fcntl.h>
#include <unistd.h>
#include <dirent.h>

#include <netinet/in.h>
#include <sys/socket.h>
#include <arpa/inet.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <pthread.h>
#include <semaphore.h>

#include "syscalls_functions.h"

#define FILENAME1 "syscalls.txt"
#define FILENAME2 "syscalls2.txt"
#define FILENAMEX "hopefully_no_such_filename_exists.txt"
#define SYMLINK1 "syscalls.symlink"
#define SYMLINK2 "syscalls2.symlink"
#define LINK1 "syscalls.link"
#define LINK2 "syscalls2.link"
#define DIR "syscalls_dir"

#define IP_ADDRESS INADDR_ANY
#define PORT 25588



/*
   CHECKAPI
   
ALL_COMMANDS = set(["socket", "bind", "connect", "sendto", "send", 
                    "recvfrom", "recv", "getsockname", "getpeername", 
                    "listen", "accept", "getsockopt", "setsockopt", 
                    "shutdown", "close", "fstatfs", "statfs", "access", 
                    "chdir", "mkdir", "rmdir", "link", "unlink", "stat", 
                    "fstat", "open", "creat", "lseek", "read", "write", 
                    "dup2", "dup", "fcntl", "getdents", "pipe", "eventfd", 
                    "eventfd2", "dup3", "inotify_init", "inotify_init1", 
                    "writev", "sendmsg", "sendfile", "recvmsg", "clone", 
                    "ioctl", "select", "poll"])
   
net_syscall_map = 
    {'getsockname_syscall':getsockname_syscall,
    'getpeername_syscall':getpeername_syscall,
    'listen_syscall':listen_syscall,          
    'accept_syscall':accept_syscall,          
    'getsockopt_syscall':getsockopt_syscall,  
    'setsockopt_syscall':setsockopt_syscall,  
'setshutdown_syscall':setshutdown_syscall,
    'socket_syscall':socket_syscall,          
    'bind_syscall':bind_syscall,              
    'connect_syscall':connect_syscall,        
    'sendto_syscall':sendto_syscall,          
    'send_syscall':send_syscall,              
    'recvfrom_syscall':recvfrom_syscall,      
    'recv_syscall':recv_syscall}



fs_syscall_map =
    {'access_syscall':access_syscall,
    'chdir_syscall':chdir_syscall,
    'close_syscall':close_syscall,
    'creat_syscall':creat_syscall,
    'dup2_syscall':dup2_syscall,
    'dup_syscall':dup_syscall,
    'fcntl_syscall':fcntl_syscall,
    'fstat_syscall':fstat_syscall,
    'fstatfs_syscall':fstatfs_syscall,
    'getdents_syscall':getdents_syscall,
    'link_syscall':link_syscall,
    'lseek_syscall':lseek_syscall,
    'mkdir_syscall':mkdir_syscall,
    'open_syscall':open_syscall,
    'read_syscall':read_syscall,
    'rmdir_syscall':rmdir_syscall,
    'stat_syscall':stat_syscall,
    'statfs_syscall':statfs_syscall,
    'unlink_syscall':unlink_syscall,
    'write_syscall':write_syscall}

*/







/*
  ACCEPT
  int accept(int sockfd, struct sockaddr *addr, socklen_t *addrlen);
  
  The  accept() system call is used with connection-based socket types
  (SOCK_STREAM, SOCK_SEQPACKET).  It  extracts  the  first  connection
  request  on  the  queue  of  pending  connections  for the listening
  socket, sockfd, creates a new connected socket, and  returns  a  new
  file  descriptor referring to that socket.  The newly created socket
  is not in the listening state.  The original socket sockfd is  unaf‐
  fected by this call.

  The  argument  sockfd  is  a  socket  that  has  been  created  with
  socket(2), bound to a local address with bind(2), and  is  listening
  for connections after a listen(2).

  The argument addr is a pointer to a sockaddr structure.  This struc‐
  ture is filled in with the address of the peer socket, as  known  to
  the  communications layer.  The exact format of the address returned
  addr is determined by the socket's address family (see socket(2) and
  the  respective  protocol man pages).  When addr is NULL, nothing is
  filled in; in this case, addrlen is not used,  and  should  also  be
  NULL.
   
*/
int execute_accept() {
  
  execute_connect();
  
  return 0;
} // execute_accept


/*
  ACCEPT4
  
  
*/
int execute_accept4() {
  
  return 0;
} // execute_accept4


/*
  ACCESS
  int access(const char *pathname, int mode);
  
  access()  checks  whether  the  calling  process can access the file
  pathname.  If pathname is a symbolic link, it is dereferenced.
  
  The mode specifies the accessibility check(s) to be  performed,  and
  is  either the value F_OK, or a mask consisting of the bitwise OR of
  one or more of R_OK, W_OK, and X_OK.  F_OK tests for  the  existence
  of  the file.  R_OK, W_OK, and X_OK test whether the file exists and
  grants read, write, and execute permissions, respectively.
  
  
*/
int execute_access() {
  // check if file exists and if noe create it.
  if(access(FILENAME1, F_OK) != 0)
    open_rdwr(FILENAME1);
  
  // check read and write access.
  access(FILENAME1, R_OK | W_OK);
  
  // check execute access.
  access(FILENAME1, X_OK);
  
  return 0;
} // execute_access


/*
  ACCT
  
  
*/
int execute_acct() {
  
  return 0;
} // execute_acct


/*
  ADD_KEY
  
  
*/
int execute_add_key() {
  
  return 0;
} // execute_add_key


/*
  ADJTIMEX
  
  
*/
int execute_adjtimex() {
  
  return 0;
} // execute_adjtimex


/*
  AFS_SYSCALL
  
  
*/
int execute_afs_syscall() {
  
  return 0;
} // execute_afs_syscall


/*
  ALARM
  
  
*/
int execute_alarm() {
  
  return 0;
} // execute_alarm


/*
  ALLOC_HUGEPAGES
  
  
*/
int execute_alloc_hugepages() {
  
  return 0;
} // execute_alloc_hugepages


/*
  BDFLUSH
  
  
*/
int execute_bdflush() {
  
  return 0;
} // execute_bdflush


/*
  BIND
  int bind(int sockfd, const struct sockaddr *addr,
                socklen_t addrlen);
  
  When  a  socket is created with socket(2), it exists in a name space
  (address family) but has no address assigned to it.  bind()  assigns
  the  address  specified  to by addr to the socket referred to by the
  file descriptor sockfd.  addrlen specifies the size,  in  bytes,  of
  the address structure pointed to by addr.  Traditionally, this oper‐
  ation is called “assigning a name to a socket”.
  
  It is normally necessary to assign  a  local  address  using  bind()
  before a SOCK_STREAM socket may receive connections (see accept(2)).
  
*/
int execute_bind() {
  // open a new socket fd.
  int sfd = socket(AF_INET, SOCK_STREAM, 0);
  
  struct sockaddr_in sin;
  memset((void *)&sin, 0, sizeof(sin));
  sin.sin_family      = AF_INET;
  sin.sin_addr.s_addr = htonl(IP_ADDRESS);
  sin.sin_port        = htons(PORT);
  
  bind(sfd, (struct sockaddr *)&sin, sizeof(sin));
  
  return 0;
} // execute_bind


/*
  BREAK
  
  
*/
int execute_break() {
  
  return 0;
} // execute_break


/*
  BRK
  
  
*/
int execute_brk() {
  
  return 0;
} // execute_brk


/*
  CACHEFLUSH
  
  
*/
int execute_cacheflush() {
  
  return 0;
} // execute_cacheflush


/*
  CAPGET
  
  
*/
int execute_capget() {
  
  return 0;
} // execute_capget


/*
  CAPSET
  
  
*/
int execute_capset() {
  
  return 0;
} // execute_capset


/*
  CHDIR
  int chdir(const char *path);
  
  chdir() changes the current working directory of the calling process
  to the directory specified in path.
  
*/
int execute_chdir() {
  // use current directory in chdir.
  chdir(".");
  
  return 0;
} // execute_chdir


/*
  CHMOD
  
  
*/
int execute_chmod() {
  
  return 0;
} // execute_chmod


/*
  CHOWN
  
  
*/
int execute_chown() {
  
  return 0;
} // execute_chown


/*
  CHOWN32
  
  
*/
int execute_chown32() {
  
  return 0;
} // execute_chown32


/*
  CHROOT
  
  
*/
int execute_chroot() {
  
  return 0;
} // execute_chroot


/*
  CLOCK_GETRES
  
  
*/
int execute_clock_getres() {
  
  return 0;
} // execute_clock_getres


/*
  CLOCK_GETTIME
  
  
*/
int execute_clock_gettime() {
  
  return 0;
} // execute_clock_gettime


/*
  CLOCK_NANOSLEEP
  
  
*/
int execute_clock_nanosleep() {
  
  return 0;
} // execute_clock_nanosleep


/*
  CLOCK_SETTIME
  
  
*/
int execute_clock_settime() {
  
  return 0;
} // execute_clock_settime


/*
  CLONE
  
  
*/
int execute_clone() {
  
  return 0;
} // execute_clone


/*
   CLOSE
   int close(int fd);
   
   close() closes a file descriptor, so that it no longer refers to any
   file and may be reused. Any record locks (see fcntl(2)) held on the
   file it  was associated with, and owned by the process, are removed
   (regardless of the file descriptor that was used to obtain the lock)

   If  fd  is the last file descriptor referring to the underlying open
   file description (see open(2)), the resources  associated  with  the
   open file description are freed; if the descriptor was the last ref‐
   erence to a file which has been removed using unlink(2) the file  is
   deleted.
   
   close()  returns  zero  on  success.   On error, -1 is returned, and
   errno is set appropriately.
 */
int execute_close() {
  // open a new file and close it.
  close(open_rdonly(FILENAME1));
  
  // open another file and then close it.
  int fd = open_rdwr(FILENAME2);
  close(fd);
  
  // try to close the same file descriptor again.
  close(fd);
  
  return 0;
} // execute_close

/*
 * A pthread that acts as a server.
 *
 */
void * start_server_thread(void *arg) {
  int sockfd = socket(AF_INET, SOCK_STREAM, 0);
  struct sockaddr_in serv_addr;
  memset((void *)&serv_addr, 0, sizeof(serv_addr));
  serv_addr.sin_family      = AF_INET;
  serv_addr.sin_addr.s_addr = htonl(IP_ADDRESS);
  serv_addr.sin_port        = htons(PORT);
  bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr));
  listen(sockfd, 5);
  
  struct sockaddr_in cli_addr;
  socklen_t clilen = sizeof(cli_addr);
  accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);
  
  return NULL;
} // start_server_thread

/*
 * Helper function that starts a new thread which acts as a
 * server. Used to test connect.
 *
 */
void start_server() {
  pthread_t pth;
  pthread_create(&pth, NULL, start_server_thread, NULL);
  sleep(1); // allow server to reach accept
} // start_server

/*
  CONNECT
  int connect(int sockfd, const struct sockaddr *addr,
                   socklen_t addrlen);
  
  The  connect()  system  call  connects the socket referred to by the
  file descriptor sockfd  to  the  address  specified  by  addr.   The
  addrlen  argument  specifies  the  size  of addr.  The format of the
  address in addr is determined by the address  space  of  the  socket
  sockfd; see socket(2) for further details.
  
*/
int execute_connect() {
  start_server();
  
  // open a new socket fd.
  int sfd = socket(AF_INET, SOCK_STREAM, 0);
  
  struct sockaddr_in sin;
  memset((void *)&sin, 0, sizeof(sin));
  sin.sin_family      = AF_INET;
  sin.sin_addr.s_addr = htonl(IP_ADDRESS);
  sin.sin_port        = htons(PORT);
  
  socklen_t sin_len = sizeof(struct sockaddr);
  connect(sfd, (struct sockaddr *)&sin, sin_len);
  sleep(3); // allow server's accept to complete.
  return 0;
} // execute_connect


/*
  CREAT
  int creat(const char *pathname, mode_t mode);
  
  creat()   is   equivalent   to   open()   with   flags   equal    to
  O_CREAT|O_WRONLY|O_TRUNC.
  
*/
int execute_creat() {
  
  creat(FILENAME1, 0666);
  creat(FILENAME2, 0600);
  
  return 0;
} // execute_creat


/*
  CREATE_MODULE
  
  
*/
int execute_create_module() {
  
  return 0;
} // execute_create_module


/*
  DELETE_MODULE
  
  
*/
int execute_delete_module() {
  
  return 0;
} // execute_delete_module


/*
   DUP
   int dup(int oldfd);
   
   This system call creates a copy of the file descriptor oldfd.

   dup()  uses  the  lowest-numbered  unused  descriptor  for  the  new
   descriptor.
   
   After  a  successful  return from one of these system calls, the old
   and new file descriptors may be used interchangeably.  They refer to
   the  same  open  file  description (see open(2)) and thus share file
   offset and file status flags; for example, if  the  file  offset  is
   modified  by using lseek(2) on one of the descriptors, the offset is
   also changed for the other.
   
   On success, these system call returns the new descriptor.  On error,
   -1 is returned, and errno is set appropriately.
 */
int execute_dup() {
  // open a new fd and duplicate it.
  int fd = open_rdonly(FILENAME1);
  dup(fd);
  
  // close this fd and try to duplicate it again.
  close(fd);
  dup(fd);
  
  return 0;
} // execute_dup


/*
   DUP2
   int dup2(int oldfd, int newfd);
   
   This system call creates a copy of the file descriptor oldfd.
   
   dup2() makes newfd be the copy of oldfd, closing newfd first if nec‐
   essary, but note the following:
   *  If oldfd is not a valid file descriptor, then the call fails, and
      newfd is not closed.
   *  If oldfd is a valid file descriptor, and newfd has the same value
      as oldfd, then dup2() does nothing, and returns newfd.
 */
int execute_dup2() {
  // open two new fds and use dup2
  int oldfd = open_rdonly(FILENAME1);
  int newfd = open_rdwr(FILENAME2);
  dup2(oldfd, newfd);
  
  // try running dup2 with oldfd=newfd
  // this should do nothing.
  dup2(oldfd, oldfd);
  
  // try running dup2 with newfd = -1 (invalid)
  dup2(oldfd, -1);
  
  // try running dup2 with newfd = closed fd
  close(newfd);
  dup2(oldfd, newfd);
  
  close(oldfd);
  dup2(oldfd, newfd);
  
  
  return 0;
} // execute_dup2


/*
   DUP3
   int dup3(int oldfd, int newfd, int flags);
   
   This system call creates a copy of the file descriptor oldfd.
   
   dup3() is the same as dup2(), except that:
   *  The caller can force the close-on-exec flag to be set for the new
      file  descriptor  by  specifying  O_CLOEXEC  in  flags.   See the
      description of the same flag in open(2) for reasons why this  may
      be useful.
   *  If oldfd equals newfd, then dup3() fails with the error EINVAL.
   
 */
int execute_dup3() {
  return 0;
} // execute_dup3


/*
  EPOLL_CREATE
  
  
*/
int execute_epoll_create() {
  
  return 0;
} // execute_epoll_create


/*
  EPOLL_CREATE1
  
  
*/
int execute_epoll_create1() {
  
  return 0;
} // execute_epoll_create1


/*
  EPOLL_CTL
  
  
*/
int execute_epoll_ctl() {
  
  return 0;
} // execute_epoll_ctl


/*
  EPOLL_PWAIT
  
  
*/
int execute_epoll_pwait() {
  
  return 0;
} // execute_epoll_pwait


/*
  EPOLL_WAIT
  
  
*/
int execute_epoll_wait() {
  
  return 0;
} // execute_epoll_wait


/*
  EVENTFD
  
  
*/
int execute_eventfd() {
  
  return 0;
} // execute_eventfd


/*
  EVENTFD2
  
  
*/
int execute_eventfd2() {
  
  return 0;
} // execute_eventfd2


/*
  EXECVE
  
  
*/
int execute_execve() {
  
  return 0;
} // execute_execve


/*
  EXIT
  
  
*/
int execute_exit() {
  
  return 0;
} // execute_exit


/*
  EXIT_GROUP
  
  
*/
int execute_exit_group() {
  
  return 0;
} // execute_exit_group


/*
  FACCESSAT
  
  
*/
int execute_faccessat() {
  
  return 0;
} // execute_faccessat


/*
  FADVISE64
  
  
*/
int execute_fadvise64() {
  
  return 0;
} // execute_fadvise64


/*
  FADVISE64_64
  
  
*/
int execute_fadvise64_64() {
  
  return 0;
} // execute_fadvise64_64


/*
  FALLOCATE
  
  
*/
int execute_fallocate() {
  
  return 0;
} // execute_fallocate


/*
  FCHDIR
  int fchdir(int fd);
  
  fchdir()  is  identical  to chdir(); the only difference is that the
  directory is given as an open file descriptor.
  
*/
int execute_fchdir() {
  // get fd for current directory and use fchdir
  int dfd = open(".", O_RDONLY);
  fchdir(dfd);
  
  return 0;
} // execute_fchdir


/*
  FCHMOD
  
  
*/
int execute_fchmod() {
  
  return 0;
} // execute_fchmod


/*
  FCHMODAT
  
  
*/
int execute_fchmodat() {
  
  return 0;
} // execute_fchmodat


/*
  FCHOWN
  
  
*/
int execute_fchown() {
  
  return 0;
} // execute_fchown


/*
  FCHOWN32
  
  
*/
int execute_fchown32() {
  
  return 0;
} // execute_fchown32


/*
  FCHOWNAT
  
  
*/
int execute_fchownat() {
  
  return 0;
} // execute_fchownat


/*
  FCNTL
  int fcntl(int fd, int cmd, ... );
  
  fcntl()  performs  one of the operations described below on the open
  file descriptor fd.  The operation is determined by cmd.
  
*/
int execute_fcntl() {
  // run fcntl with F_GETFL on a read only file.
  fcntl(open_rdonly(FILENAME1) , F_GETFL);
  
  // run fcntl with F_GETFL on a read-write file.
  fcntl(open_rdwr(FILENAME2) , F_GETFL);
  
  
  return 0;
} // execute_fcntl


/*
  FCNTL64
  
  
*/
int execute_fcntl64() {
  
  return 0;
} // execute_fcntl64


/*
  FDATASYNC
  
  
*/
int execute_fdatasync() {
  
  return 0;
} // execute_fdatasync


/*
  FGETXATTR
  
  
*/
int execute_fgetxattr() {
  
  return 0;
} // execute_fgetxattr


/*
  FLISTXATTR
  
  
*/
int execute_flistxattr() {
  
  return 0;
} // execute_flistxattr


/*
  FLOCK
  
  
*/
int execute_flock() {
  
  return 0;
} // execute_flock


/*
  FORK
  
  
*/
int execute_fork() {
  
  return 0;
} // execute_fork


/*
  FREE_HUGEPAGES
  
  
*/
int execute_free_hugepages() {
  
  return 0;
} // execute_free_hugepages


/*
  FREMOVEXATTR
  
  
*/
int execute_fremovexattr() {
  
  return 0;
} // execute_fremovexattr


/*
  FSETXATTR
  
  
*/
int execute_fsetxattr() {
  
  return 0;
} // execute_fsetxattr


/*
   FSTAT
   int fstat(int fd, struct stat *buf);
   
   fstat()  is  identical to stat(), except that the file to be stat-ed
   is specified by the file descriptor fd.
   
 */
int execute_fstat() {
  struct stat fileStat;
  
  // open a file and run fstat.
  int fd = open_rdonly(FILENAME1);
  fstat(fd, &fileStat);
  
  // close fd and run fstat again.
  close(fd);
  fstat(fd, &fileStat);
  
  return 0;
} // execute_fstat


/*
  FSTAT64
  
  
*/
int execute_fstat64() {
  
  return 0;
} // execute_fstat64


/*
  FSTATAT64
  
  
*/
int execute_fstatat64() {
  
  return 0;
} // execute_fstatat64


/*
  FSTATVFS
  int fstatvfs(int fd, struct statvfs *buf);
  
*/
int execute_fstatvfs() {
  struct statvfs fileStat;
  
  // open a file and run fstat.
  int fd = open_rdonly(FILENAME1);
  fstatvfs(fd, &fileStat);
  
  return 0;
} // execute_fstatvfs


/*
  FSTATVFS64
  
  
*/
int execute_fstatvfs64() {
  
  return 0;
} // execute_fstatvfs64


/*
  FSYNC
  
  
*/
int execute_fsync() {
  
  return 0;
} // execute_fsync


/*
  FTIME
  
  
*/
int execute_ftime() {
  
  return 0;
} // execute_ftime


/*
  FTRUNCATE
  
  
*/
int execute_ftruncate() {
  
  return 0;
} // execute_ftruncate


/*
  FTRUNCATE64
  
  
*/
int execute_ftruncate64() {
  
  return 0;
} // execute_ftruncate64


/*
  FUTEX
  
  
*/
int execute_futex() {
  
  return 0;
} // execute_futex


/*
  FUTIMESAT
  
  
*/
int execute_futimesat() {
  
  return 0;
} // execute_futimesat


/*
  GET_KERNEL_SYMS
  
  
*/
int execute_get_kernel_syms() {
  
  return 0;
} // execute_get_kernel_syms


/*
  GET_MEMPOLICY
  
  
*/
int execute_get_mempolicy() {
  
  return 0;
} // execute_get_mempolicy


/*
  GET_ROBUST_LIST
  
  
*/
int execute_get_robust_list() {
  
  return 0;
} // execute_get_robust_list


/*
  GET_THREAD_AREA
  
  
*/
int execute_get_thread_area() {
  
  return 0;
} // execute_get_thread_area


/*
  GETCPU
  
  
*/
int execute_getcpu() {
  
  return 0;
} // execute_getcpu


/*
  GETCWD
  
  
*/
int execute_getcwd() {
  
  return 0;
} // execute_getcwd


/*
  GETDENTS
  int getdents(unsigned int fd, struct linux_dirent *dirp,
                    unsigned int count);
                    
  The  system  call  getdents()  reads several linux_dirent structures
  from the directory referred to by the open file descriptor  fd  into
  the  buffer  pointed  to  by dirp.  The argument count specifies the
  size of that buffer.            
  
*/
int execute_getdents() {
  return 0;
} // execute_getdents


/*
  GETDENTS64
  
  
*/
int execute_getdents64() {
  
  return 0;
} // execute_getdents64


/*
  GETEGID
  
  
*/
int execute_getegid() {
  
  return 0;
} // execute_getegid


/*
  GETEGID32
  
  
*/
int execute_getegid32() {
  
  return 0;
} // execute_getegid32


/*
  GETEUID
  
  
*/
int execute_geteuid() {
  
  return 0;
} // execute_geteuid


/*
  GETEUID32
  
  
*/
int execute_geteuid32() {
  
  return 0;
} // execute_geteuid32


/*
  GETGID
  
  
*/
int execute_getgid() {
  
  return 0;
} // execute_getgid


/*
  GETGID32
  
  
*/
int execute_getgid32() {
  
  return 0;
} // execute_getgid32


/*
  GETGROUPS
  
  
*/
int execute_getgroups() {
  
  return 0;
} // execute_getgroups


/*
  GETGROUPS32
  
  
*/
int execute_getgroups32() {
  
  return 0;
} // execute_getgroups32


/*
  GETITIMER
  
  
*/
int execute_getitimer() {
  
  return 0;
} // execute_getitimer


/*
  GETPEERNAME
  int   getpeername(int   sockfd,  struct  sockaddr  *addr,  socklen_t
       *addrlen);
  
  getpeername() returns the address  of  the  peer  connected  to  the
  socket  sockfd, in the buffer pointed to by addr.  The addrlen argu‐
  ment should be initialized to indicate the amount of  space  pointed
  to  by  addr.   On  return  it  contains the actual size of the name
  returned (in bytes).  The name is truncated if the  buffer  provided
  is too small.
  
*/
int execute_getpeername() {
  start_server();
  
  // open a new socket fd.
  int sfd = socket(AF_INET, SOCK_STREAM, 0);
  
  struct sockaddr_in sin;
  memset((void *)&sin, 0, sizeof(sin));
  sin.sin_family      = AF_INET;
  sin.sin_addr.s_addr = htonl(IP_ADDRESS);
  sin.sin_port        = htons(PORT);
  
  socklen_t sin_len = sizeof(struct sockaddr);
  connect(sfd, (struct sockaddr *)&sin, sin_len);
  
  socklen_t len = sizeof(struct sockaddr);
  struct sockaddr_in sock;
  getpeername(sfd, (struct sockaddr *)&sock, &len);
  
  return 0;
} // execute_getpeername


/*
  GETPAGESIZE
  
  
*/
int execute_getpagesize() {
  
  return 0;
} // execute_getpagesize


/*
  GETPGID
  
  
*/
int execute_getpgid() {
  
  return 0;
} // execute_getpgid


/*
  GETPGRP
  
  
*/
int execute_getpgrp() {
  
  return 0;
} // execute_getpgrp


/*
  GETPID
  
  
*/
int execute_getpid() {
  
  return 0;
} // execute_getpid


/*
  GETPMSG
  
  
*/
int execute_getpmsg() {
  
  return 0;
} // execute_getpmsg


/*
  GETPPID
  
  
*/
int execute_getppid() {
  
  return 0;
} // execute_getppid


/*
  GETPRIORITY
  
  
*/
int execute_getpriority() {
  
  return 0;
} // execute_getpriority


/*
  GETRESGID
  
  
*/
int execute_getresgid() {
  
  return 0;
} // execute_getresgid


/*
  GETRESGID32
  
  
*/
int execute_getresgid32() {
  
  return 0;
} // execute_getresgid32


/*
  GETRESUID
  
  
*/
int execute_getresuid() {
  
  return 0;
} // execute_getresuid


/*
  GETRESUID32
  
  
*/
int execute_getresuid32() {
  
  return 0;
} // execute_getresuid32


/*
  GETRLIMIT
  
  
*/
int execute_getrlimit() {
  
  return 0;
} // execute_getrlimit


/*
  GETRUSAGE
  
  
*/
int execute_getrusage() {
  
  return 0;
} // execute_getrusage


/*
  GETSID
  
  
*/
int execute_getsid() {
  
  return 0;
} // execute_getsid


/*
  GETSOCKNAME
  int getsockname(int sockfd, struct sockaddr *addr
                  , socklen_t *addrlen);
                  
  getsockname() returns the current address to which the socket sockfd
  is bound, in the buffer pointed to by addr.   The  addrlen  argument
  should  be  initialized  to  indicate the amount of space (in bytes)
  pointed to by addr.  On return it contains the actual  size  of  the
  socket address.             
  
*/
int execute_getsockname() {
  // open a new socket fd.
  int sfd = socket(AF_INET, SOCK_STREAM, 0);
  
  struct sockaddr_in sin;
  memset((void *)&sin, 0, sizeof(sin));
  sin.sin_family      = AF_INET;
  sin.sin_addr.s_addr = htonl(IP_ADDRESS);
  sin.sin_port        = htons(PORT);
  
  bind(sfd, (struct sockaddr *)&sin, sizeof(sin));
  
  socklen_t len = sizeof(struct sockaddr);
  struct sockaddr_in sock;
  getsockname(sfd, (struct sockaddr *)&sock, &len);
  
  return 0;
} // execute_getsockname


/*
  GETSOCKOPT
  int getsockopt(int sockfd, int level, int optname,
                 void *optval, socklen_t *optlen);
  
  getsockopt()  and  setsockopt()  manipulate  options  for the socket
  referred to by the file descriptor sockfd.   Options  may  exist  at
  multiple  protocol  levels; they are always present at the uppermost
  socket level.
  
*/
int execute_getsockopt() {
  int sfd = socket(AF_INET, SOCK_STREAM, 0);
  int optval;
  socklen_t optlen = sizeof(optval);
  
  getsockopt(sfd, SOL_SOCKET, SO_TYPE, &optval, &optlen);
  getsockopt(sfd, SOL_SOCKET, SO_OOBINLINE, &optval, &optlen);
  return 0;
} // execute_getsockopt


/*
  GETTID
  
  
*/
int execute_gettid() {
  
  return 0;
} // execute_gettid


/*
  GETTIMEOFDAY
  
  
*/
int execute_gettimeofday() {
  
  return 0;
} // execute_gettimeofday


/*
  GETUID
  
  
*/
int execute_getuid() {
  
  return 0;
} // execute_getuid


/*
  GETUID32
  
  
*/
int execute_getuid32() {
  
  return 0;
} // execute_getuid32


/*
  GETXATTR
  
  
*/
int execute_getxattr() {
  
  return 0;
} // execute_getxattr


/*
  GTTY
  
  
*/
int execute_gtty() {
  
  return 0;
} // execute_gtty


/*
  IDLE
  
  
*/
int execute_idle() {
  
  return 0;
} // execute_idle


/*
  INIT_MODULE
  
  
*/
int execute_init_module() {
  
  return 0;
} // execute_init_module


/*
  INOTIFY_ADD_WATCH
  
  
*/
int execute_inotify_add_watch() {
  
  return 0;
} // execute_inotify_add_watch


/*
  INOTIFY_INIT
  
  
*/
int execute_inotify_init() {
  
  return 0;
} // execute_inotify_init


/*
  INOTIFY_INIT1
  
  
*/
int execute_inotify_init1() {
  
  return 0;
} // execute_inotify_init1


/*
  INOTIFY_RM_WATCH
  
  
*/
int execute_inotify_rm_watch() {
  
  return 0;
} // execute_inotify_rm_watch


/*
  IO_CANCEL
  
  
*/
int execute_io_cancel() {
  
  return 0;
} // execute_io_cancel


/*
  IO_DESTROY
  
  
*/
int execute_io_destroy() {
  
  return 0;
} // execute_io_destroy


/*
  IO_GETEVENTS
  
  
*/
int execute_io_getevents() {
  
  return 0;
} // execute_io_getevents


/*
  IO_SETUP
  
  
*/
int execute_io_setup() {
  
  return 0;
} // execute_io_setup


/*
  IO_SUBMIT
  
  
*/
int execute_io_submit() {
  
  return 0;
} // execute_io_submit


/*
  IOCTL
  
  
*/
int execute_ioctl() {
  
  return 0;
} // execute_ioctl


/*
  IOPERM
  
  
*/
int execute_ioperm() {
  
  return 0;
} // execute_ioperm


/*
  IOPL
  
  
*/
int execute_iopl() {
  
  return 0;
} // execute_iopl


/*
  IOPRIO_GET
  
  
*/
int execute_ioprio_get() {
  
  return 0;
} // execute_ioprio_get


/*
  IOPRIO_SET
  
  
*/
int execute_ioprio_set() {
  
  return 0;
} // execute_ioprio_set


/*
  IPC
  
  
*/
int execute_ipc() {
  
  return 0;
} // execute_ipc


/*
  KEXEC_LOAD
  
  
*/
int execute_kexec_load() {
  
  return 0;
} // execute_kexec_load


/*
  KEYCTL
  
  
*/
int execute_keyctl() {
  
  return 0;
} // execute_keyctl


/*
  KILL
  
  
*/
int execute_kill() {
  
  return 0;
} // execute_kill


/*
  LCHOWN
  
  
*/
int execute_lchown() {
  
  return 0;
} // execute_lchown


/*
  LCHOWN32
  
  
*/
int execute_lchown32() {
  
  return 0;
} // execute_lchown32


/*
  LGETXATTR
  
  
*/
int execute_lgetxattr() {
  
  return 0;
} // execute_lgetxattr


/*
  LINK
  int link(const char *oldpath, const char *newpath);
  
  link() creates a new link (also known as a hard link) to an existing
  file.
  
  If newpath exists it will not be overwritten.
  
  This new name may be used exactly as the old one for any  operation;
  both  names refer to the same file (and so have the same permissions
  and ownership) and it is impossible  to  tell  which  name  was  the
  "original".
  
*/
int execute_link() {
  // make sure the file exists and run link
  close(open_rdonly(FILENAME1));
  link(FILENAME1, LINK1);
  
  // run link on a non existing file.
  link(FILENAMEX, LINK2);
  
  // run link on an already existing link filename.
  close(open_rdonly(FILENAME2));
  link(FILENAME2, LINK1);
  
  return 0;
} // execute_link


/*
  LINKAT
  
  
*/
int execute_linkat() {
  
  return 0;
} // execute_linkat


/*
  LISTEN
  int listen(int sockfd, int backlog);
  
  listen() marks the socket referred to by sockfd as a passive socket,
  that is, as a socket that will be used to accept incoming connection
  requests using accept(2).

  The  sockfd argument is a file descriptor that refers to a socket of
  type SOCK_STREAM or SOCK_SEQPACKET.

  The backlog argument defines the maximum length to which  the  queue
  of pending connections for sockfd may grow.  If a connection request
  arrives when the queue is full, the client may receive an error with
  an  indication  of  ECONNREFUSED or, if the underlying protocol sup‐
  ports retransmission, the request may be ignored  so  that  a  later
  reattempt at connection succeeds.
  
*/
int execute_listen() {
  
  execute_connect();
  
  return 0;
} // execute_listen


/*
  LISTXATTR
  
  
*/
int execute_listxattr() {
  
  return 0;
} // execute_listxattr


/*
  LLISTXATTR
  
  
*/
int execute_llistxattr() {
  
  return 0;
} // execute_llistxattr


/*
  LOCK
  
  
*/
int execute_lock() {
  
  return 0;
} // execute_lock


/*
  LOOKUP_DCOOKIE
  
  
*/
int execute_lookup_dcookie() {
  
  return 0;
} // execute_lookup_dcookie


/*
  LREMOVEXATTR
  
  
*/
int execute_lremovexattr() {
  
  return 0;
} // execute_lremovexattr


/*
  LSEEK
  off_t lseek(int fd, off_t offset, int whence);
  
  The lseek() function repositions the offset of the open file associ‐
  ated with the file descriptor fd to the argument offset according to
  the directive whence as follows:
  
*/
int execute_lseek() {
  int fd = open_rdwr(FILENAME1);
  write(fd, "abcdefghijklmnopqrstuvwxyz", 26);
  char buffer[10];
  
  // set the offset to the second character.
  lseek(fd, 1, SEEK_SET);
  read(fd, buffer,10);
  
  // set the offeset to 5 characters after the current offset.
  lseek(fd, 5, SEEK_CUR);
  read(fd, buffer,10);
  
  return 0;
} // execute_lseek


/*
  LSETXATTR
  
  
*/
int execute_lsetxattr() {
  
  return 0;
} // execute_lsetxattr


/*
   LSTAT
   int lstat(const char *path, struct stat *buf);
   
   lstat()  is  identical  to stat(), except that if path is a symbolic
   link, then the link itself is stat-ed, not the file that  it  refers
   to.
      
   On  success,  zero is returned.  On error, -1 is returned, and errno
   is set appropriately.
   
 */
int execute_lstat() {
  struct stat fileStat;
  
  // make sure the symlink exists and run lstat
  close(open_rdonly(FILENAME1));
  symlink(FILENAME1, SYMLINK1);
  lstat(SYMLINK1, &fileStat);
  
  /*
  printf("Information for %s\n", filename);
  printf("---------------------------\n");
  printf("File Size: \t\t%d bytes\n", fileStat.st_size);
  printf("Number of Links: \t%d\n", fileStat.st_nlink);
  printf("File inode: \t\t%d\n", fileStat.st_ino);

  printf("File Permissions: \t");
  printf( (S_ISDIR(fileStat.st_mode)) ? "d" : "-");
  printf( (fileStat.st_mode & S_IRUSR) ? "r" : "-");
  printf( (fileStat.st_mode & S_IWUSR) ? "w" : "-");
  printf( (fileStat.st_mode & S_IXUSR) ? "x" : "-");
  printf( (fileStat.st_mode & S_IRGRP) ? "r" : "-");
  printf( (fileStat.st_mode & S_IWGRP) ? "w" : "-");
  printf( (fileStat.st_mode & S_IXGRP) ? "x" : "-");
  printf( (fileStat.st_mode & S_IROTH) ? "r" : "-");
  printf( (fileStat.st_mode & S_IWOTH) ? "w" : "-");
  printf( (fileStat.st_mode & S_IXOTH) ? "x" : "-");
  printf("\n\n");
  
  printf("The file %s a symbolic link\n"
         , (S_ISLNK(fileStat.st_mode)) ? "is" : "is not");
  */
  
  return 0;
} // execute_lstat


/*
  LSTAT64
  
  
*/
int execute_lstat64() {
  
  return 0;
} // execute_lstat64


/*
  MADVISE
  
  
*/
int execute_madvise() {
  
  return 0;
} // execute_madvise


/*
  MADVISE1
  
  
*/
int execute_madvise1() {
  
  return 0;
} // execute_madvise1


/*
  MBIND
  
  
*/
int execute_mbind() {
  
  return 0;
} // execute_mbind


/*
  MIGRATE_PAGES
  
  
*/
int execute_migrate_pages() {
  
  return 0;
} // execute_migrate_pages


/*
  MINCORE
  
  
*/
int execute_mincore() {
  
  return 0;
} // execute_mincore


/*
  MKDIR
  int mkdir(const char *pathname, mode_t mode);
  
  mkdir() attempts to create a directory named pathname.
  
*/
int execute_mkdir() {
  // create a new directory with 0775
  mkdir(DIR, S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
  
  // mkdir on existing dir
  mkdir(DIR, S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
  
  return 0;
} // execute_mkdir


/*
  MKDIRAT
  
  
*/
int execute_mkdirat() {
  
  return 0;
} // execute_mkdirat


/*
  MKNOD
  
  
*/
int execute_mknod() {
  
  return 0;
} // execute_mknod


/*
  MKNODAT
  
  
*/
int execute_mknodat() {
  
  return 0;
} // execute_mknodat


/*
  MLOCK
  
  
*/
int execute_mlock() {
  
  return 0;
} // execute_mlock


/*
  MLOCKALL
  
  
*/
int execute_mlockall() {
  
  return 0;
} // execute_mlockall


/*
  MMAP
  
  
*/
int execute_mmap() {
  
  return 0;
} // execute_mmap


/*
  MMAP2
  
  
*/
int execute_mmap2() {
  
  return 0;
} // execute_mmap2


/*
  MODIFY_LDT
  
  
*/
int execute_modify_ldt() {
  
  return 0;
} // execute_modify_ldt


/*
  MOUNT
  
  
*/
int execute_mount() {
  
  return 0;
} // execute_mount


/*
  MOVE_PAGES
  
  
*/
int execute_move_pages() {
  
  return 0;
} // execute_move_pages


/*
  MPROTECT
  
  
*/
int execute_mprotect() {
  
  return 0;
} // execute_mprotect


/*
  MPX
  
  
*/
int execute_mpx() {
  
  return 0;
} // execute_mpx


/*
  MQ_GETSETATTR
  
  
*/
int execute_mq_getsetattr() {
  
  return 0;
} // execute_mq_getsetattr


/*
  MQ_NOTIFY
  
  
*/
int execute_mq_notify() {
  
  return 0;
} // execute_mq_notify


/*
  MQ_OPEN
  
  
*/
int execute_mq_open() {
  
  return 0;
} // execute_mq_open


/*
  MQ_TIMEDRECEIVE
  
  
*/
int execute_mq_timedreceive() {
  
  return 0;
} // execute_mq_timedreceive


/*
  MQ_TIMEDSEND
  
  
*/
int execute_mq_timedsend() {
  
  return 0;
} // execute_mq_timedsend


/*
  MQ_UNLINK
  
  
*/
int execute_mq_unlink() {
  
  return 0;
} // execute_mq_unlink


/*
  MREMAP
  
  
*/
int execute_mremap() {
  
  return 0;
} // execute_mremap


/*
  MSGCTL
  
  
*/
int execute_msgctl() {
  
  return 0;
} // execute_msgctl


/*
  MSGGET
  
  
*/
int execute_msgget() {
  
  return 0;
} // execute_msgget


/*
  MSGRCV
  
  
*/
int execute_msgrcv() {
  
  return 0;
} // execute_msgrcv


/*
  MSGSND
  
  
*/
int execute_msgsnd() {
  
  return 0;
} // execute_msgsnd


/*
  MSYNC
  
  
*/
int execute_msync() {
  
  return 0;
} // execute_msync


/*
  MUNLOCK
  
  
*/
int execute_munlock() {
  
  return 0;
} // execute_munlock


/*
  MUNLOCKALL
  
  
*/
int execute_munlockall() {
  
  return 0;
} // execute_munlockall


/*
  MUNMAP
  
  
*/
int execute_munmap() {
  
  return 0;
} // execute_munmap


/*
  NANOSLEEP
  
  
*/
int execute_nanosleep() {
  
  return 0;
} // execute_nanosleep


/*
  NFSSERVCTL
  
  
*/
int execute_nfsservctl() {
  
  return 0;
} // execute_nfsservctl


/*
  NICE
  
  
*/
int execute_nice() {
  
  return 0;
} // execute_nice


/*
  OLDFSTAT
  
  
*/
int execute_oldfstat() {
  
  return 0;
} // execute_oldfstat


/*
  OLDLSTAT
  
  
*/
int execute_oldlstat() {
  
  return 0;
} // execute_oldlstat


/*
  OLDOLDUNAME
  
  
*/
int execute_oldolduname() {
  
  return 0;
} // execute_oldolduname


/*
  OLDSTAT
  
  
*/
int execute_oldstat() {
  
  return 0;
} // execute_oldstat


/*
  OLDUNAME
  
  
*/
int execute_olduname() {
  
  return 0;
} // execute_olduname


/* 
 * helper functions that open a file and return their file descriptor.
 *
 */
int open_rdonly(char* filename) {
  return open(filename, O_RDONLY | O_CREAT
              , S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH);
} // open_rdonly

int open_rdwr(char* filename) {
  return open(filename, O_RDWR | O_CREAT | O_APPEND
              , S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH);
} // open_rdwr

/*
  OPEN
  int open(const char *pathname, int flags);
  int open(const char *pathname, int flags, mode_t mode);
  
  Given  a  pathname  for  a file, open() returns a file descriptor, a
  small, nonnegative  integer  for  use  in  subsequent  system  calls
  
  The file descriptor returned by a successful call will be  the 
  lowest-numbered file descriptor not currently open for the process.
  
  A call to open() creates a new open file description, an entry in
  the system-wide table of open files. This entry records the file
  offset and the file status flags. A file descriptor is a reference
  to one of these entries.
  
  The argument flags must include one of the following access modes:
  O_RDONLY, O_WRONLY or O_RDWR. These request opening the file read-
  only, write-only, or read/write, respectively.
 
  O_RDONLY, O_WRONLY, O_RDWR
  O_APPEND    - The file is opened in append mode. Before each write,
                the file  offset is positioned at the end of the file.
  O_ASYNC     - Enable signal-driven  I/O.
  O_CLOEXEC   - Enable  the close-on-exec flag for the new file
                descriptor.
  O_CREAT     - If the file does not exist it will be created. Mode
                must be specified when O_CREAT is used.
  O_DIRECT    - Try to minimize cache effects of the I/O to and from
                this file
  O_DIRECTORY - If pathname is not a directory, cause the open to fail.
  O_EXCL      - Ensure that this call creates the file: if this flag is
                specified  in  conjunction with O_CREAT, and pathname
                already exists, then open() will fail.
  O_LARGEFILE - Allow  files  whose  sizes cannot be represented in an
                off_t (but can be represented in an off64_t) to be
                opened.
  O_NOATIME   - Do not update the file last access time when the file
                is read.
  O_NOCTTY    - If pathname refers to a terminal device it will not
                become the process's controlling terminal even if the
                process does not have one.
  O_NOFOLLOW  - If pathname is a symbolic link, then the open fails
  O_NONBLOCK  - When possible, the file is opened in nonblocking mode.
  O_NDELAY    - When possible, the file is opened in nonblocking mode.
  O_SYNC      - The file is opened for synchronous I/O.
  O_TRUNC     - If the file already exists and is a regular file and
                the open mode allows writing (i.e., is O_RDWR or
                O_WRONLY) it will  be truncated to length 0.
*/
int execute_open() {
  // open a file for reading with O_CREATE.
  open_rdonly(FILENAME1);
  
  // open a file for reading and writing with O_CREATE and O_APPEND
  open_rdwr(FILENAME2);
  
  // try to open a file without O_CREATE, that hopefully does not
  // exist.
  open(FILENAMEX
       , O_RDONLY , S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH);
       
  return 0;
} // execute_open


/*
  OPENAT
  
  
*/
int execute_openat() {
  
  return 0;
} // execute_openat


/*
  PAUSE
  
  
*/
int execute_pause() {
  
  return 0;
} // execute_pause


/*
  PCICONFIG_IOBASE
  
  
*/
int execute_pciconfig_iobase() {
  
  return 0;
} // execute_pciconfig_iobase


/*
  PCICONFIG_READ
  
  
*/
int execute_pciconfig_read() {
  
  return 0;
} // execute_pciconfig_read


/*
  PCICONFIG_WRITE
  
  
*/
int execute_pciconfig_write() {
  
  return 0;
} // execute_pciconfig_write


/*
  PERF_EVENT_OPEN
  
  
*/
int execute_perf_event_open() {
  
  return 0;
} // execute_perf_event_open


/*
  PERSONALITY
  
  
*/
int execute_personality() {
  
  return 0;
} // execute_personality


/*
  PHYS
  
  
*/
int execute_phys() {
  
  return 0;
} // execute_phys


/*
  PIPE
  
  
*/
int execute_pipe() {
  
  return 0;
} // execute_pipe


/*
  PIPE2
  
  
*/
int execute_pipe2() {
  
  return 0;
} // execute_pipe2


/*
  PIVOT_ROOT
  
  
*/
int execute_pivot_root() {
  
  return 0;
} // execute_pivot_root


/*
  POLL
  
  
*/
int execute_poll() {
  
  return 0;
} // execute_poll


/*
  PPOLL
  
  
*/
int execute_ppoll() {
  
  return 0;
} // execute_ppoll


/*
  PRCTL
  
  
*/
int execute_prctl() {
  
  return 0;
} // execute_prctl


/*
  PREAD64
  
  
*/
int execute_pread64() {
  
  return 0;
} // execute_pread64


/*
  PREADV
  
  
*/
int execute_preadv() {
  
  return 0;
} // execute_preadv


/*
  PRLIMIT
  
  
*/
int execute_prlimit() {
  
  return 0;
} // execute_prlimit


/*
  PROF
  
  
*/
int execute_prof() {
  
  return 0;
} // execute_prof


/*
  PROFIL
  
  
*/
int execute_profil() {
  
  return 0;
} // execute_profil


/*
  PSELECT6
  
  
*/
int execute_pselect6() {
  
  return 0;
} // execute_pselect6


/*
  PTRACE
  
  
*/
int execute_ptrace() {
  
  return 0;
} // execute_ptrace


/*
  PUTPMSG
  
  
*/
int execute_putpmsg() {
  
  return 0;
} // execute_putpmsg


/*
  PWRITE64
  
  
*/
int execute_pwrite64() {
  
  return 0;
} // execute_pwrite64


/*
  PWRITEV
  
  
*/
int execute_pwritev() {
  
  return 0;
} // execute_pwritev


/*
  QUERY_MODULE
  
  
*/
int execute_query_module() {
  
  return 0;
} // execute_query_module


/*
  QUOTACTL
  
  
*/
int execute_quotactl() {
  
  return 0;
} // execute_quotactl


/*
  READ
  ssize_t read(int fd, void *buf, size_t count);
  
  read()  attempts  to  read up to count bytes from file descriptor fd
  into the buffer starting at buf.
   
*/
int execute_read() {
  // write a sample text
  int fd = open_rdwr(FILENAME1);
  char* value = "Sample output text\n";
  size_t sizeOfValue = strlen(value) * sizeof(char);
  write(fd, value, sizeOfValue);
  close(fd);
  
  char data[20];
  read(open_rdonly(FILENAME1), data, 20);

  return 0;
} // execute_read


/*
  READAHEAD
  
  
*/
int execute_readahead() {
  
  return 0;
} // execute_readahead


/*
  READDIR
  
  
*/
int execute_readdir() {
  
  return 0;
} // execute_readdir


/*
  READLINK
  
  
*/
int execute_readlink() {
  
  return 0;
} // execute_readlink


/*
  READLINKAT
  
  
*/
int execute_readlinkat() {
  
  return 0;
} // execute_readlinkat


/*
  READV
  
  
*/
int execute_readv() {
  
  return 0;
} // execute_readv


/*
  REBOOT
  
  
*/
int execute_reboot() {
  
  return 0;
} // execute_reboot


/*
 * A pthread that acts as a server.
 * A helper method that starts a server ans sends a message
 * to the client it receives an access request from.
 *
 */
void * server_send_thread(void *message) {
  int sockfd = socket(AF_INET, SOCK_STREAM, 0);
  struct sockaddr_in serv_addr;
  memset((void *)&serv_addr, 0, sizeof(serv_addr));
  serv_addr.sin_family      = AF_INET;
  serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
  serv_addr.sin_port        = htons(PORT);
  bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr));
  listen(sockfd, 5);
  
  struct sockaddr_in cli_addr;
  socklen_t clilen = sizeof(cli_addr);
  int cl = accept(sockfd, (struct sockaddr *) &cli_addr, &clilen);
  
  size_t  messagelen = strlen(message)+1;
  send(cl, message, messagelen, 0);
  
  return NULL;
} // server_send_thread

/*
 * Helper function that starts a new thread which acts as a
 * server and sends the given message. Used to test recv.
 *
 */
void server_send(char *message) {
  pthread_t pth;
  pthread_create(&pth, NULL, server_send_thread, message);
  sleep(3);
} // server_send


/*
  RECV
  ssize_t recv(int sockfd, void *buf, size_t len, int flags);
  
  Receive a message from a socket
  The recv() call is normally used only on  a  connected  socket  (see
  connect(2))  and  is  identical  to  recvfrom() with a NULL src_addr
  argument.
  
*/
int execute_recv() {
  char* message = "Message to be received.";
  size_t  messagelen = strlen(message)+1;
  server_send(message);
  
  // open a new socket fd.
  int sfd = socket(AF_INET, SOCK_STREAM, 0);
  
  struct sockaddr_in sin;
  memset((void *)&sin, 0, sizeof(sin));
  sin.sin_family      = AF_INET;
  sin.sin_addr.s_addr = htonl(IP_ADDRESS);
  sin.sin_port        = htons(PORT);
  
  socklen_t sin_len = sizeof(struct sockaddr);
  connect(sfd, (struct sockaddr *)&sin, sin_len);
  
  char line[messagelen];
  recv(sfd, line, messagelen, 0);
  sleep(3);
  return 0;
} // execute_recv


/*
 * A pthread that acts as a server.
 * A helper method that starts a server ans sends a message
 * to the client it receives an access request from.
 *
 */
void * server_recvfrom_thread(void * arg) {
  struct sockaddr_in si_me, si_other;
	
	int s;
	socklen_t slen = sizeof(si_other);
	char buf[512];
	
	//create a UDP socket
	s=socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
	
	// zero out the structure
	memset((char *) &si_me, 0, sizeof(si_me));
	
	si_me.sin_family = AF_INET;
	si_me.sin_port = htons(PORT);
	si_me.sin_addr.s_addr = htonl(INADDR_ANY);
	
	bind(s , (struct sockaddr*)&si_me, sizeof(si_me));
	
  recvfrom(s, buf, 512, 0, 
                (struct sockaddr *) &si_other, &slen);
  sleep(3);
  return NULL;
} // server_recvfrom_thread

/*
 * Helper function that starts a new thread which acts as a
 * server and sends the given message. Used to test recv.
 *
 */
void server_recvfrom() {
  pthread_t pth;
  pthread_create(&pth, NULL, server_recvfrom_thread, NULL);
  sleep(3);
} // server_recvfrom

/*
  RECVFROM
  ssize_t recvfrom(int sockfd, void *buf, size_t len, int flags,
                   struct sockaddr *src_addr, socklen_t *addrlen);
  
*/
int execute_recvfrom() {
	server_recvfrom();
	execute_sendto();
	sleep(3);
	
	return 0;
} // execute_recvfrom


/*
  RECVMSG
  
  
*/
int execute_recvmsg() {
  
  return 0;
} // execute_recvmsg


/*
  RECVMMSG
  
  
*/
int execute_recvmmsg() {
  
  return 0;
} // execute_recvmmsg


/*
  REMAP_FILE_PAGES
  
  
*/
int execute_remap_file_pages() {
  
  return 0;
} // execute_remap_file_pages


/*
  REMOVEXATTR
  
  
*/
int execute_removexattr() {
  
  return 0;
} // execute_removexattr


/*
  RENAME
  
  
*/
int execute_rename() {
  
  return 0;
} // execute_rename


/*
  RENAMEAT
  
  
*/
int execute_renameat() {
  
  return 0;
} // execute_renameat


/*
  REQUEST_KEY
  
  
*/
int execute_request_key() {
  
  return 0;
} // execute_request_key


/*
  RESTART_SYSCALL
  
  
*/
int execute_restart_syscall() {
  
  return 0;
} // execute_restart_syscall


/*
  RMDIR
  int rmdir(const char *pathname);
  
  rmdir() deletes a directory, which must be empty.
  
*/
int execute_rmdir() {
  // make sure the directory exists and remove it.
  mkdir(DIR, S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
  rmdir(DIR);
  
  return 0;
} // execute_rmdir


/*
  RT_SIGACTION
  
  
*/
int execute_rt_sigaction() {
  
  return 0;
} // execute_rt_sigaction


/*
  RT_SIGPENDING
  
  
*/
int execute_rt_sigpending() {
  
  return 0;
} // execute_rt_sigpending


/*
  RT_SIGPROCMASK
  
  
*/
int execute_rt_sigprocmask() {
  
  return 0;
} // execute_rt_sigprocmask


/*
  RT_SIGQUEUEINFO
  
  
*/
int execute_rt_sigqueueinfo() {
  
  return 0;
} // execute_rt_sigqueueinfo


/*
  RT_SIGRETURN
  
  
*/
int execute_rt_sigreturn() {
  
  return 0;
} // execute_rt_sigreturn


/*
  RT_SIGSUSPEND
  
  
*/
int execute_rt_sigsuspend() {
  
  return 0;
} // execute_rt_sigsuspend


/*
  RT_SIGTIMEDWAIT
  
  
*/
int execute_rt_sigtimedwait() {
  
  return 0;
} // execute_rt_sigtimedwait


/*
  RT_TGSIGQUEUEINFO
  
  
*/
int execute_rt_tgsigqueueinfo() {
  
  return 0;
} // execute_rt_tgsigqueueinfo


/*
  SCHED_GET_PRIORITY_MAX
  
  
*/
int execute_sched_get_priority_max() {
  
  return 0;
} // execute_sched_get_priority_max


/*
  SCHED_GET_PRIORITY_MIN
  
  
*/
int execute_sched_get_priority_min() {
  
  return 0;
} // execute_sched_get_priority_min


/*
  SCHED_GETAFFINITY
  
  
*/
int execute_sched_getaffinity() {
  
  return 0;
} // execute_sched_getaffinity


/*
  SCHED_GETPARAM
  
  
*/
int execute_sched_getparam() {
  
  return 0;
} // execute_sched_getparam


/*
  SCHED_GETSCHEDULER
  
  
*/
int execute_sched_getscheduler() {
  
  return 0;
} // execute_sched_getscheduler


/*
  SCHED_RR_GET_INTERVAL
  
  
*/
int execute_sched_rr_get_interval() {
  
  return 0;
} // execute_sched_rr_get_interval


/*
  SCHED_SETAFFINITY
  
  
*/
int execute_sched_setaffinity() {
  
  return 0;
} // execute_sched_setaffinity


/*
  SCHED_SETPARAM
  
  
*/
int execute_sched_setparam() {
  
  return 0;
} // execute_sched_setparam


/*
  SCHED_SETSCHEDULER
  
  
*/
int execute_sched_setscheduler() {
  
  return 0;
} // execute_sched_setscheduler


/*
  SCHED_YIELD
  
  
*/
int execute_sched_yield() {
  
  return 0;
} // execute_sched_yield


/*
  SECURITY
  
  
*/
int execute_security() {
  
  return 0;
} // execute_security


/*
  SELECT
  
  
*/
int execute_select() {
  
  return 0;
} // execute_select


/*
  SEMCTL
  
  
*/
int execute_semctl() {
  
  return 0;
} // execute_semctl


/*
  SEMGET
  
  
*/
int execute_semget() {
  
  return 0;
} // execute_semget


/*
  SEMOP
  
  
*/
int execute_semop() {
  
  return 0;
} // execute_semop


/*
  SEMTIMEDOP
  
  
*/
int execute_semtimedop() {
  
  return 0;
} // execute_semtimedop


/*
  SEND
  ssize_t send(int sockfd, const void *buf, size_t len, int flags);
  
  The  system calls send(), sendto(), and sendmsg() are used to trans‐
  mit a message to another socket.
  
  The send() call may be used only when the socket is in  a  connected
  state  (so  that the intended recipient is known).  The only differ‐
  ence between send() and write(2) is the presence of flags.   With  a
  zero  flags  argument,  send() is equivalent to write(2).
  
*/
int execute_send() {
  start_server();
  
  // open a new socket fd.
  int sfd = socket(AF_INET, SOCK_STREAM, 0);
  
  struct sockaddr_in sin;
  memset((void *)&sin, 0, sizeof(sin));
  sin.sin_family      = AF_INET;
  sin.sin_addr.s_addr = htonl(IP_ADDRESS);
  sin.sin_port        = htons(PORT);
  
  socklen_t sin_len = sizeof(struct sockaddr);
  connect(sfd, (struct sockaddr *)&sin, sin_len);
  
  int send_num = htonl(25588);
  send(sfd, &send_num, sizeof(send_num), 0);
  
  // send secret message out of band
  char* secret_message = "None shall be revealed";
  send(sfd, secret_message, strlen(secret_message)+1, MSG_OOB);
  
  return 0;
} // execute_send


/*
  SENDFILE
  
  
*/
int execute_sendfile() {
  
  return 0;
} // execute_sendfile


/*
  SENDFILE64
  
  
*/
int execute_sendfile64() {
  
  return 0;
} // execute_sendfile64


/*
  SENDMSG
  ssize_t sendmsg(int sockfd, const struct msghdr *msg, int flags);
  
  For sendmsg(), the message is pointed to by  the  elements  of
  the  array  msg.msg_iov.   The  sendmsg()  call  also allows sending
  ancillary data (also known as control information).
  
*/
int execute_sendmsg() {
  int sfd = socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP);
  
  struct sockaddr_in sin;
  memset((void *)&sin, 0, sizeof(sin));
  sin.sin_family      = AF_INET;
  sin.sin_addr.s_addr = htonl(IP_ADDRESS);
  sin.sin_port        = htons(PORT);
   
  struct msghdr msg;
  struct iovec iov;
  
  char* message = "Message for sendmsg.";
  msg.msg_name = &sin;
  msg.msg_namelen = sizeof(sin);
  msg.msg_iov = &iov;
  msg.msg_iovlen = 1;
  msg.msg_iov->iov_base = message;
  msg.msg_iov->iov_len = strlen(message)+1;
  
  sendmsg(sfd, &msg, 0);

  return 0;
} // execute_sendmsg


/*
  SENDTO
  ssize_t sendto(int sockfd, const void *buf, size_t len, int flags,
                 const struct sockaddr *dest_addr, socklen_t addrlen);
  
  The  system calls send(), sendto(), and sendmsg() are used to trans‐
  mit a message to another socket.
  
*/
int execute_sendto() {
  int sfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
  
  struct sockaddr_in sin;
  memset((void *)&sin, 0, sizeof(sin));
  sin.sin_family      = AF_INET;
  sin.sin_addr.s_addr = htonl(IP_ADDRESS);
  sin.sin_port        = htons(PORT);
  
  char* message = "Message for sendto.";
  sendto(sfd, message, strlen(message)+1, 0,
        (struct sockaddr*)&sin, sizeof(sin));
  
  return 0;
} // execute_sendto


/*
  SET_MEMPOLICY
  
  
*/
int execute_set_mempolicy() {
  
  return 0;
} // execute_set_mempolicy


/*
  SET_ROBUST_LIST
  
  
*/
int execute_set_robust_list() {
  
  return 0;
} // execute_set_robust_list


/*
  SET_THREAD_AREA
  
  
*/
int execute_set_thread_area() {
  
  return 0;
} // execute_set_thread_area


/*
  SET_TID_ADDRESS
  
  
*/
int execute_set_tid_address() {
  
  return 0;
} // execute_set_tid_address


/*
  SET_ZONE_RECLAIM
  
  
*/
int execute_set_zone_reclaim() {
  
  return 0;
} // execute_set_zone_reclaim


/*
  SETDOMAINNAME
  
  
*/
int execute_setdomainname() {
  
  return 0;
} // execute_setdomainname


/*
  SETFSGID
  
  
*/
int execute_setfsgid() {
  
  return 0;
} // execute_setfsgid


/*
  SETFSGID32
  
  
*/
int execute_setfsgid32() {
  
  return 0;
} // execute_setfsgid32


/*
  SETFSUID
  
  
*/
int execute_setfsuid() {
  
  return 0;
} // execute_setfsuid


/*
  SETFSUID32
  
  
*/
int execute_setfsuid32() {
  
  return 0;
} // execute_setfsuid32


/*
  SETGID
  
  
*/
int execute_setgid() {
  
  return 0;
} // execute_setgid


/*
  SETGID32
  
  
*/
int execute_setgid32() {
  
  return 0;
} // execute_setgid32


/*
  SETGROUPS
  
  
*/
int execute_setgroups() {
  
  return 0;
} // execute_setgroups


/*
  SETGROUPS32
  
  
*/
int execute_setgroups32() {
  
  return 0;
} // execute_setgroups32


/*
  SETHOSTNAME
  
  
*/
int execute_sethostname() {
  
  return 0;
} // execute_sethostname


/*
  SETITIMER
  
  
*/
int execute_setitimer() {
  
  return 0;
} // execute_setitimer


/*
  SETPGID
  
  
*/
int execute_setpgid() {
  
  return 0;
} // execute_setpgid


/*
  SETPRIORITY
  
  
*/
int execute_setpriority() {
  
  return 0;
} // execute_setpriority


/*
  SETREGID
  
  
*/
int execute_setregid() {
  
  return 0;
} // execute_setregid


/*
  SETREGID32
  
  
*/
int execute_setregid32() {
  
  return 0;
} // execute_setregid32


/*
  SETRESGID
  
  
*/
int execute_setresgid() {
  
  return 0;
} // execute_setresgid


/*
  SETRESGID32
  
  
*/
int execute_setresgid32() {
  
  return 0;
} // execute_setresgid32


/*
  SETRESUID
  
  
*/
int execute_setresuid() {
  
  return 0;
} // execute_setresuid


/*
  SETRESUID32
  
  
*/
int execute_setresuid32() {
  
  return 0;
} // execute_setresuid32


/*
  SETREUID
  
  
*/
int execute_setreuid() {
  
  return 0;
} // execute_setreuid


/*
  SETREUID32
  
  
*/
int execute_setreuid32() {
  
  return 0;
} // execute_setreuid32


/*
  SETRLIMIT
  
  
*/
int execute_setrlimit() {
  
  return 0;
} // execute_setrlimit


/*
  SETSID
  
  
*/
int execute_setsid() {
  
  return 0;
} // execute_setsid


/*
  SETSOCKOPT
  int setsockopt(int sockfd, int level, int optname,
                 const void *optval, socklen_t optlen);
  
  getsockopt()  and  setsockopt()  manipulate  options  for the socket
  referred to by the file descriptor sockfd.   Options  may  exist  at
  multiple  protocol  levels; they are always present at the uppermost
  socket level.
  
*/
int execute_setsockopt() {
  int sfd = socket(AF_INET, SOCK_STREAM, 0);
  int optval = 1;
  socklen_t optlen = sizeof(optval);
  
  struct sockaddr_in sin;
  memset((void *)&sin, 0, sizeof(sin));
  sin.sin_family      = AF_INET;
  sin.sin_addr.s_addr = htonl(IP_ADDRESS);
  sin.sin_port        = htons(PORT);

  bind(sfd, (struct sockaddr *)&sin, sizeof(struct sockaddr_in));
  
  setsockopt(sfd, SOL_SOCKET, SO_REUSEADDR, (char*)&optval, optlen);
  
  return 0;
} // execute_setsockopt


/*
  SETTIMEOFDAY
  
  
*/
int execute_settimeofday() {
  
  return 0;
} // execute_settimeofday


/*
  SETUID
  
  
*/
int execute_setuid() {
  
  return 0;
} // execute_setuid


/*
  SETUID32
  
  
*/
int execute_setuid32() {
  
  return 0;
} // execute_setuid32


/*
  SETUP
  
  
*/
int execute_setup() {
  
  return 0;
} // execute_setup


/*
  SETXATTR
  
  
*/
int execute_setxattr() {
  
  return 0;
} // execute_setxattr


/*
  SGETMASK
  
  
*/
int execute_sgetmask() {
  
  return 0;
} // execute_sgetmask


/*
  SHMAT
  
  
*/
int execute_shmat() {
  
  return 0;
} // execute_shmat


/*
  SHMCTL
  
  
*/
int execute_shmctl() {
  
  return 0;
} // execute_shmctl


/*
  SHMDT
  
  
*/
int execute_shmdt() {
  
  return 0;
} // execute_shmdt


/*
  SHMGET
  
  
*/
int execute_shmget() {
  
  return 0;
} // execute_shmget


/*
  SHUTDOWN
  int shutdown(int sockfd, int how);
  
  The  shutdown()  call causes all or part of a full-duplex connection
  on the socket associated with sockfd to be shut  down.   If  how  is
  SHUT_RD,  further receptions will be disallowed.  If how is SHUT_WR,
  further transmissions will be disallowed.  If how is SHUT_RDWR, fur‐
  ther receptions and transmissions will be disallowed.
  
*/
int execute_shutdown() {
  start_server();
  
  // open a new socket fd.
  int sfd = socket(AF_INET, SOCK_STREAM, 0);
  
  struct sockaddr_in sin;
  memset((void *)&sin, 0, sizeof(sin));
  sin.sin_family      = AF_INET;
  sin.sin_addr.s_addr = htonl(IP_ADDRESS);
  sin.sin_port        = htons(PORT);
  
  socklen_t sin_len = sizeof(struct sockaddr);
  connect(sfd, (struct sockaddr *)&sin, sin_len);
  
  shutdown(sfd, SHUT_RD);
  shutdown(sfd, SHUT_WR);
  shutdown(sfd, SHUT_RDWR);
  
  
  return 0;
} // execute_shutdown


/*
  SIGACTION
  
  
*/
int execute_sigaction() {
  
  return 0;
} // execute_sigaction


/*
  SIGALTSTACK
  
  
*/
int execute_sigaltstack() {
  
  return 0;
} // execute_sigaltstack


/*
  SIGNAL
  
  
*/
int execute_signal() {
  
  return 0;
} // execute_signal


/*
  SIGNALFD
  
  
*/
int execute_signalfd() {
  
  return 0;
} // execute_signalfd


/*
  SIGNALFD4
  
  
*/
int execute_signalfd4() {
  
  return 0;
} // execute_signalfd4


/*
  SIGPENDING
  
  
*/
int execute_sigpending() {
  
  return 0;
} // execute_sigpending


/*
  SIGPROCMASK
  
  
*/
int execute_sigprocmask() {
  
  return 0;
} // execute_sigprocmask


/*
  SIGRETURN
  
  
*/
int execute_sigreturn() {
  
  return 0;
} // execute_sigreturn


/*
  SIGSUSPEND
  
  
*/
int execute_sigsuspend() {
  
  return 0;
} // execute_sigsuspend


/*
  SOCKET
  int socket(int domain, int type, int protocol);
  
  socket()  creates  an  endpoint  for  communication  and  returns  a
  descriptor.
  
*/
int execute_socket() {
  socket(AF_INET, SOCK_STREAM, 0);
  socket(AF_INET, SOCK_DGRAM, 0);
  
  return 0;
} // execute_socket


/*
  SOCKETCALL
  
  
*/
int execute_socketcall() {
  
  return 0;
} // execute_socketcall


/*
  SOCKETPAIR
  
  
*/
int execute_socketpair() {
  
  return 0;
} // execute_socketpair


/*
  SPLICE
  
  
*/
int execute_splice() {
  
  return 0;
} // execute_splice


/*
  SPU_CREATE
  
  
*/
int execute_spu_create() {
  
  return 0;
} // execute_spu_create


/*
  SPU_RUN
  
  
*/
int execute_spu_run() {
  
  return 0;
} // execute_spu_run


/*
  SSETMASK
  
  
*/
int execute_ssetmask() {
  
  return 0;
} // execute_ssetmask


/*
   STAT
   int stat(const char *path, struct stat *buf);
   
   stat() stats the file pointed to by path and fills in buf.
   
   On  success,  zero is returned.  On error, -1 is returned, and errno
   is set appropriately.
   
 */
int execute_stat() {
  struct stat fileStat;
  
  // make sure the file exists and run stat.
  close(open_rdonly(FILENAME1));
  stat(FILENAME1, &fileStat);
  
  // run stat on a non existing file.
  stat(FILENAMEX, &fileStat);
  
  /*
  printf("Information for %s\n", filename);
  printf("---------------------------\n");
  printf("File Size: \t\t%d bytes\n", fileStat.st_size);
  printf("Number of Links: \t%d\n", fileStat.st_nlink);
  printf("File inode: \t\t%d\n", fileStat.st_ino);

  printf("File Permissions: \t");
  printf( (S_ISDIR(fileStat.st_mode)) ? "d" : "-");
  printf( (fileStat.st_mode & S_IRUSR) ? "r" : "-");
  printf( (fileStat.st_mode & S_IWUSR) ? "w" : "-");
  printf( (fileStat.st_mode & S_IXUSR) ? "x" : "-");
  printf( (fileStat.st_mode & S_IRGRP) ? "r" : "-");
  printf( (fileStat.st_mode & S_IWGRP) ? "w" : "-");
  printf( (fileStat.st_mode & S_IXGRP) ? "x" : "-");
  printf( (fileStat.st_mode & S_IROTH) ? "r" : "-");
  printf( (fileStat.st_mode & S_IWOTH) ? "w" : "-");
  printf( (fileStat.st_mode & S_IXOTH) ? "x" : "-");
  printf("\n\n");

  printf("The file %s a symbolic link\n"
  , (S_ISLNK(fileStat.st_mode)) ? "is" : "is not");
  */
  
  return 0;
} // execute_stat


/*
  STAT64
  
  
*/
int execute_stat64() {
  
  return 0;
} // execute_stat64


/*
  STATVFS
  int statvfs(const char *path, struct statvfs *buf);
  
  The function statvfs() returns information about a mounted file system.
  path is the pathname of any file within the mounted file  system.
  
*/
int execute_statvfs() {
  struct statvfs fileStat;
  
  // make sure the file exists and run stat.
  close(open_rdonly(FILENAME1));
  statvfs(FILENAME1, &fileStat);

  return 0;
} // execute_statvfs


/*
  STATVFS64
  
  
*/
int execute_statvfs64() {
  
  return 0;
} // execute_statvfs64


/*
  STIME
  
  
*/
int execute_stime() {
  
  return 0;
} // execute_stime


/*
  STTY
  
  
*/
int execute_stty() {
  
  return 0;
} // execute_stty


/*
  SUBPAGE_PROT
  
  
*/
int execute_subpage_prot() {
  
  return 0;
} // execute_subpage_prot


/*
  SWAPOFF
  
  
*/
int execute_swapoff() {
  
  return 0;
} // execute_swapoff


/*
  SWAPON
  
  
*/
int execute_swapon() {
  
  return 0;
} // execute_swapon


/*
   SYMLINK
   int symlink(const char *oldpath, const char *newpath);
   
   symlink()  creates  a symbolic link named newpath which contains the
   string oldpath.
   
   On  success,  zero is returned.  On error, -1 is returned, and errno
   is set appropriately.
 */
int execute_symlink() {
  // make sure the file exists and run symlink
  close(open_rdonly(FILENAME1));
  symlink(FILENAME1, SYMLINK1);
  
  // run symlink on a non existing file.
  symlink(FILENAMEX, SYMLINK2);
  
  // run symlink on an already existing symlink filename.
  close(open_rdonly(FILENAME2));
  symlink(FILENAME2, SYMLINK1);
  
  return 0;
} // execute_symlink


/*
  SYMLINKAT
  
  
*/
int execute_symlinkat() {
  
  return 0;
} // execute_symlinkat


/*
  SYNC
  
  
*/
int execute_sync() {
  
  return 0;
} // execute_sync


/*
  SYNC_FILE_RANGE
  
  
*/
int execute_sync_file_range() {
  
  return 0;
} // execute_sync_file_range


/*
  SYNC_FILE_RANGE2
  
  
*/
int execute_sync_file_range2() {
  
  return 0;
} // execute_sync_file_range2


/*
  SYSFS
  
  
*/
int execute_sysfs() {
  
  return 0;
} // execute_sysfs


/*
  SYSINFO
  
  
*/
int execute_sysinfo() {
  
  return 0;
} // execute_sysinfo


/*
  SYSLOG
  
  
*/
int execute_syslog() {
  
  return 0;
} // execute_syslog


/*
  TEE
  
  
*/
int execute_tee() {
  
  return 0;
} // execute_tee


/*
  TGKILL
  
  
*/
int execute_tgkill() {
  
  return 0;
} // execute_tgkill


/*
  TIME
  
  
*/
int execute_time() {
  
  return 0;
} // execute_time


/*
  TIMER_CREATE
  
  
*/
int execute_timer_create() {
  
  return 0;
} // execute_timer_create


/*
  TIMER_DELETE
  
  
*/
int execute_timer_delete() {
  
  return 0;
} // execute_timer_delete


/*
  TIMER_GETOVERRUN
  
  
*/
int execute_timer_getoverrun() {
  
  return 0;
} // execute_timer_getoverrun


/*
  TIMER_GETTIME
  
  
*/
int execute_timer_gettime() {
  
  return 0;
} // execute_timer_gettime


/*
  TIMER_SETTIME
  
  
*/
int execute_timer_settime() {
  
  return 0;
} // execute_timer_settime


/*
  TIMERFD_CREATE
  
  
*/
int execute_timerfd_create() {
  
  return 0;
} // execute_timerfd_create


/*
  TIMERFD_GETTIME
  
  
*/
int execute_timerfd_gettime() {
  
  return 0;
} // execute_timerfd_gettime


/*
  TIMERFD_SETTIME
  
  
*/
int execute_timerfd_settime() {
  
  return 0;
} // execute_timerfd_settime


/*
  TIMES
  
  
*/
int execute_times() {
  
  return 0;
} // execute_times


/*
  TKILL
  
  
*/
int execute_tkill() {
  
  return 0;
} // execute_tkill


/*
  TRUNCATE
  
  
*/
int execute_truncate() {
  
  return 0;
} // execute_truncate


/*
  TRUNCATE64
  
  
*/
int execute_truncate64() {
  
  return 0;
} // execute_truncate64


/*
  TUXCALL
  
  
*/
int execute_tuxcall() {
  
  return 0;
} // execute_tuxcall


/*
  UGETRLIMIT
  
  
*/
int execute_ugetrlimit() {
  
  return 0;
} // execute_ugetrlimit


/*
  ULIMIT
  
  
*/
int execute_ulimit() {
  
  return 0;
} // execute_ulimit


/*
  UMASK
  
  
*/
int execute_umask() {
  
  return 0;
} // execute_umask


/*
  UMOUNT
  
  
*/
int execute_umount() {
  
  return 0;
} // execute_umount


/*
  UMOUNT2
  
  
*/
int execute_umount2() {
  
  return 0;
} // execute_umount2


/*
  UNAME
  
  
*/
int execute_uname() {
  
  return 0;
} // execute_uname


/*
  UNLINK
  int unlink(const char *pathname);
  
  unlink()  deletes a name from the file system.  If that name was the
  last link to a file and no processes have the file open the file  is
  deleted and the space it was using is made available for reuse.

  If the name was the last link to a file but any processes still have
  the file open the file will remain in existence until the last  file
  descriptor referring to it is closed.

  If the name referred to a symbolic link the link is removed.

  If  the name referred to a socket, fifo or device the name for it is
  removed but processes which have the object open may continue to use
  it.
  
*/
int execute_unlink() {
  // make sure the file exists and run unlink
  close(open_rdonly(FILENAME1));
  unlink(FILENAME1);
  
  // make a symlink exists and run unlink
  close(open_rdonly(FILENAME2));
  symlink(FILENAME2, SYMLINK1);
  unlink(SYMLINK1);
  
  // unlink a non existing file
  unlink(FILENAMEX);
  
  return 0;
} // execute_unlink


/*
  UNLINKAT
  
  
*/
int execute_unlinkat() {
  
  return 0;
} // execute_unlinkat


/*
  UNSHARE
  
  
*/
int execute_unshare() {
  
  return 0;
} // execute_unshare


/*
  USELIB
  
  
*/
int execute_uselib() {
  
  return 0;
} // execute_uselib


/*
  USTAT
  
  
*/
int execute_ustat() {
  
  return 0;
} // execute_ustat


/*
  UTIME
  
  
*/
int execute_utime() {
  
  return 0;
} // execute_utime


/*
  UTIMENSAT
  
  
*/
int execute_utimensat() {
  
  return 0;
} // execute_utimensat


/*
  UTIMES
  
  
*/
int execute_utimes() {
  
  return 0;
} // execute_utimes


/*
  VFORK
  
  
*/
int execute_vfork() {
  
  return 0;
} // execute_vfork


/*
  VHANGUP
  
  
*/
int execute_vhangup() {
  
  return 0;
} // execute_vhangup


/*
  VM86OLD
  
  
*/
int execute_vm86old() {
  
  return 0;
} // execute_vm86old


/*
  VMSPLICE
  
  
*/
int execute_vmsplice() {
  
  return 0;
} // execute_vmsplice


/*
  VSERVER
  
  
*/
int execute_vserver() {
  
  return 0;
} // execute_vserver


/*
  WAIT4
  
  
*/
int execute_wait4() {
  
  return 0;
} // execute_wait4


/*
  WAITID
  
  
*/
int execute_waitid() {
  
  return 0;
} // execute_waitid


/*
  WAITPID
  
  
*/
int execute_waitpid() {
  
  return 0;
} // execute_waitpid


/*
  WRITE
  ssize_t write(int fd, const void *buf, size_t count);
  
  write()  writes up to count bytes from the buffer pointed buf to the
  file referred to by the file descriptor fd.

*/
int execute_write() {
  int fd = open_rdwr(FILENAME1);
  char* value = "Sample output text\n";
  size_t sizeOfValue = strlen(value) * sizeof(char);
  
  write(fd, value, sizeOfValue);
  
  return 0;
} // execute_write


/*
  WRITEV
  
  
*/
int execute_writev() {
  
  return 0;
} // execute_writev

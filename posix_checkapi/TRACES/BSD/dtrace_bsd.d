#!/usr/sbin/dtrace -s

#pragma D option quiet
#pragma D option switchrate=10

dtrace:::BEGIN 
{
  err[0] = "";
  err[0] = "";
  err[EPERM] = "EPERM";
  err[ENOENT] = "ENOENT";
  err[ESRCH] = "ESRCH";
  err[EINTR] = "EINTR";
  err[EIO] = "EIO";
  err[ENXIO] = "ENXIO";
  err[E2BIG] = "E2BIG";
  err[ENOEXEC] = "ENOEXEC";
  err[EBADF] = "EBADF";
  err[ECHILD] = "ECHILD";
  err[EAGAIN] = "EAGAIN";
  err[ENOMEM] = "ENOMEM";
  err[EACCES] = "EACCES";
  err[EFAULT] = "EFAULT";
  err[ENOTBLK] = "ENOTBLK";
  err[EBUSY] = "EBUSY";
  err[EEXIST] = "EEXIST";
  err[EXDEV] = "EXDEV";
  err[ENODEV] = "ENODEV";
  err[ENOTDIR] = "ENOTDIR";
  err[EISDIR] = "EISDIR";
  err[EINVAL] = "EINVAL";
  err[ENFILE] = "ENFILE";
  err[EMFILE] = "EMFILE";
  err[ENOTTY] = "ENOTTY";
  err[ETXTBSY] = "ETXTBSY";
  err[EFBIG] = "EFBIG";
  err[ENOSPC] = "ENOSPC";
  err[ESPIPE] = "ESPIPE";
  err[EROFS] = "EROFS";
  err[EMLINK] = "EMLINK";
  err[EPIPE] = "EPIPE";
  err[EDOM] = "EDOM";
  err[ERANGE] = "ERANGE";
  err[ENOMSG] = "ENOMSG";
  err[EIDRM] = "EIDRM";
  /* err[ECHRNG] = "ECHRNG";
  err[EL2NSYNC] = "EL2NSYNC";
  err[EL3HLT] = "EL3HLT";
  err[EL3RST] = "EL3RST";
  err[ELNRNG] = "ELNRNG";
  err[EUNATCH] = "EUNATCH";
  err[ENOCSI] = "ENOCSI";
  err[EL2HLT] = "EL2HLT";
  err[EDEADLK] = "EDEADLK";
  err[ENOLCK] = "ENOLCK";
  err[ECANCELED] = "ECANCELED";
  err[ENOTSUP] = "ENOTSUP";
  err[EDQUOT] = "EDQUOT";
  err[EBADE] = "EBADE";
  err[EBADR] = "EBADR";
  err[EXFULL] = "EXFULL";
  err[ENOANO] = "ENOANO";
  err[EBADRQC] = "EBADRQC";
  err[EBADSLT] = "EBADSLT";
  err[EDEADLOCK] = "EDEADLOCK";
  err[EBFONT] = "EBFONT";
  err[EOWNERDEAD] = "EOWNERDEAD";
  err[ENOTRECOVERABLE] = "ENOTRECOVERABLE";
  err[ENOSTR] = "ENOSTR";
  err[ENODATA] = "ENODATA";
  err[ETIME] = "ETIME";
  err[ENOSR] = "ENOSR";
  err[ENONET] = "ENONET";
  err[ENOPKG] = "ENOPKG";
  err[EREMOTE] = "EREMOTE";
  err[ENOLINK] = "ENOLINK";
  err[EADV] = "EADV";
  err[ESRMNT] = "ESRMNT";
  err[ECOMM] = "ECOMM";
  err[EPROTO] = "EPROTO";
  err[ELOCKUNMAPPED] = "ELOCKUNMAPPED";
  err[ENOTACTIVE] = "ENOTACTIVE";
  err[EMULTIHOP] = "EMULTIHOP";
  err[EBADMSG] = "EBADMSG";
  err[ENAMETOOLONG] = "ENAMETOOLONG";
  err[EOVERFLOW] = "EOVERFLOW";
  err[ENOTUNIQ] = "ENOTUNIQ";
  err[EBADFD] = "EBADFD";
  err[EREMCHG] = "EREMCHG";
  err[ELIBACC] = "ELIBACC";
  err[ELIBBAD] = "ELIBBAD";
  err[ELIBSCN] = "ELIBSCN";
  err[ELIBMAX] = "ELIBMAX";
  err[ELIBEXEC] = "ELIBEXEC";
  err[EILSEQ] = "EILSEQ";
  err[ENOSYS] = "ENOSYS";
  err[ELOOP] = "ELOOP";
  err[ERESTART] = "ERESTART";
  err[ESTRPIPE] = "ESTRPIPE";
  err[ENOTEMPTY] = "ENOTEMPTY";
  err[EUSERS] = "EUSERS";
  err[ENOTSOCK] = "ENOTSOCK";
  err[EDESTADDRREQ] = "EDESTADDRREQ";
  err[EMSGSIZE] = "EMSGSIZE";
  err[EPROTOTYPE] = "EPROTOTYPE";
  err[ENOPROTOOPT] = "ENOPROTOOPT";
  err[EPROTONOSUPPORT] = "EPROTONOSUPPORT";
  err[ESOCKTNOSUPPORT] = "ESOCKTNOSUPPORT";
  err[EOPNOTSUPP] = "EOPNOTSUPP";
  err[EPFNOSUPPORT] = "EPFNOSUPPORT";
  err[EAFNOSUPPORT] = "EAFNOSUPPORT";
  err[EADDRINUSE] = "EADDRINUSE";
  err[EADDRNOTAVAIL] = "EADDRNOTAVAIL";
  err[ENETDOWN] = "ENETDOWN";
  err[ENETUNREACH] = "ENETUNREACH";
  err[ENETRESET] = "ENETRESET";
  err[ECONNABORTED] = "ECONNABORTED";
  err[ECONNRESET] = "ECONNRESET";
  err[ENOBUFS] = "ENOBUFS";
  err[EISCONN] = "EISCONN";
  err[ENOTCONN] = "ENOTCONN";
  err[ESHUTDOWN] = "ESHUTDOWN";
  err[ETOOMANYREFS] = "ETOOMANYREFS";
  err[ETIMEDOUT] = "ETIMEDOUT";
  err[ECONNREFUSED] = "ECONNREFUSED";
  err[EHOSTDOWN] = "EHOSTDOWN";
  err[EHOSTUNREACH] = "EHOSTUNREACH";
  err[EWOULDBLOCK] = "EWOULDBLOCK";
  err[EALREADY] = "EALREADY";
  err[EINPROGRESS] = "EINPROGRESS";
  err[ESTALE] = "ESTALE";*/
}


/* ===ACCEPT/GETSOCKNAME/GETPEERNAME===
 * int getsockname(int  s,  struct  sockaddr  *name,  socklen_t *namelen);
 * int getpeername(int  s,  struct  sockaddr  *name,  socklen_t *namelen);
 * int      accept(int  s,  struct  sockaddr  *addr,  socklen_t *addrlen);
 */
syscall::*getsockname*:entry,
syscall::*getpeername*:entry,
syscall::*accept*:entry
/pid != $pid/
{
  self->start = timestamp;
  self->arg0 = arg0;
  self->arg1 = arg1;
  self->arg2 = arg2;
}

syscall::*getsockname*:return,
syscall::*getpeername*:return,
syscall::*accept*:return
/self->start && pid != $pid/
{
  this->sock = (struct sockaddr_in *) copyin(self->arg1, sizeof(struct sockaddr));
  
  self->family = this->sock->sin_family;

  self->port = ntohs(this->sock->sin_port);
  
  this->a = (uint8_t *)&this->sock->sin_addr;
  this->addr1 = strjoin(lltostr(this->a[0] + 0ULL), strjoin(".",
  strjoin(lltostr(this->a[1] + 0ULL), ".")));
  this->addr2 = strjoin(lltostr(this->a[2] + 0ULL), strjoin(".",
  lltostr(this->a[3] + 0ULL)));
  self->ip = strjoin(this->addr1, this->addr2);
  
  self->len = *(socklen_t *) copyin(self->arg2, sizeof(socklen_t));
            
  printf("%d ", pid);
  printf("%s", probefunc);
  printf("(%d, {sa_family=%d, sin_port=htons(%d), sin_addr=inet_addr(\"%s\")}, %d)\t\t "
         , self->arg0
         , self->family
         , self->port
         , self->ip
         , self->len);
  
  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->arg1 = 0;
  self->arg2 = 0;
  self->start = 0;
}


/* ===ACCESS===
 * int access(const char *path, int amode);
 * int  mkdir(const char *path, mode_t mode);
 * int creat(const char *path, mode_t mode);
 *
 */
syscall::*access*:entry,
syscall::*mkdir*:entry,
syscall::*creat*:entry
/pid != $pid/
{
  self->start = timestamp;
  self->arg0 = arg0;
  self->arg1 = arg1;
}
syscall::*access*:return,
syscall::*mkdir*:return,
syscall::*creat*:return
/self->start && pid != $pid/
{
  printf("%d ", pid);
  printf("%s", probefunc);
  printf("(\"%S\", %d)\t\t "
         , copyinstr(self->arg0)
         , self->arg1);
  
  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->arg1 = 0;
  self->start = 0;
}


/* ===BIND/CONNECT===
 * int bind(int s, const struct sockaddr *name, int namelen);
 * int connect(int s, const struct sockaddr *name, int namelen);
 *
 */
syscall::*bind*:entry,
syscall::*connect*:entry
/pid != $pid/
{
  self->start = timestamp;
  self->arg0 = arg0;
  self->arg1 = arg1;
  self->arg2 = arg2;
  
}
syscall::*bind*:return,
syscall::*connect*:return
/self->start && pid != $pid/
{
  this->sock = (struct sockaddr_in *) copyin(
                 self->arg1, sizeof(struct sockaddr));
  
  self->family = this->sock->sin_family;

  self->port = ntohs(this->sock->sin_port);
  
  this->a = (uint8_t *)&this->sock->sin_addr;
  this->addr1 = strjoin(lltostr(this->a[0] + 0ULL), strjoin(".",
  strjoin(lltostr(this->a[1] + 0ULL), ".")));
  this->addr2 = strjoin(lltostr(this->a[2] + 0ULL), strjoin(".",
  lltostr(this->a[3] + 0ULL)));
  
  self->ip = strjoin(this->addr1, this->addr2);
  
  
  printf("%d ", pid);
  printf("%s", probefunc);
  printf("(%d, {sa_family=%d, sin_port=htons(%d), sin_addr=inet_addr(\"%s\")}, %d)\t\t "
         , self->arg0
         , self->family
         , self->port
         , self->ip
         , self->arg2);
  
  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->arg1 = 0;
  self->arg2 = 0;
  self->start = 0;
}


/* ===CHDIR/RMDIR/UNLINK===
 * int chdir(const char *path);
 * int rmdir(const char *path);
 * int unlink(const char *path);
 * 
 * 
 */
syscall::chdir*:entry,
syscall::rmdir*:entry,
syscall::unlink*:entry
/pid != $pid/
{
  self->start = timestamp;
  self->arg0 = arg0;
}
syscall::chdir*:return,
syscall::rmdir*:return,
syscall::unlink*:return
/self->start && pid != $pid/
{
  printf("%d ", pid);
  printf("%s", probefunc);
  printf("(\"%S\")\t\t "
         , copyinstr(self->arg0));
  
  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->start = 0;
}


/* ===CLOSE/DUP===
 * int close(int fd);
 */
syscall::*close*:entry,
syscall::*dup:entry
/pid != $pid/
{
  self->start = timestamp;
  self->arg0 = arg0;
}
syscall::*close*:return,
syscall::*dup:return
/self->start && pid != $pid/
{
  printf("%d ", pid);
  printf("%s", probefunc);
  printf("(%d)\t\t "
         , self->arg0);
  
  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->start = 0;
}


/* ===DUP2===
 * int dup2(int oldfd, int newfd);
 */
syscall::dup2*:entry
/pid != $pid/
{
  self->start = timestamp;
  self->arg0 = arg0;
  self->arg1 = arg1;
}
syscall::dup2*:return
/self->start && pid != $pid/
{
  printf("%d ", pid);
  printf("%s", probefunc);
  printf("(%d, %d)\t\t "
         , self->arg0
         , self->arg1);
  
  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->start = 0;
}


/* ===FCNTL===
 * int fcntl(int fildes, int cmd, / arg / ...);
 *
 */
syscall::fcntl*:entry
/pid != $pid/
{
  self->start = timestamp;
  self->arg0 = arg0;
  self->arg1 = arg1;
  self->arg2 = arg2;
}
syscall::fcntl*:return
/self->start && pid != $pid/
{
  printf("%d ", pid);
  printf("%s(%d, %d, %d)\t\t " , probefunc
                       , self->arg0
                       , self->arg1
                       , self->arg2);
  
  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->start = 0;
}


/* ===FSTAT===
 * int fstat(int fd, struct stat *buf);
 *
 */
syscall::fstat:entry
/pid != $pid/
{
  self->start = timestamp;
  self->arg0 = arg0;
  self->arg1 = arg1;
}

syscall::fstat:return
/self->start && pid != $pid/
{
  this->stat = (struct stat*) copyin((uintptr_t) self->arg1, sizeof(struct stat));
  
  printf("%d ", pid);
  printf("%s(%d, {st_dev=%d, st_ino=%d, st_mode=%d, st_nlink=%d, st_uid=%d, st_gid=%d, st_blksize=%d, st_blocks=%d, st_size=%d, st_atime=%d, st_mtime=%d, st_ctime=%d})\t\t ", 
                  probefunc,
                  self->arg0,
                  this->stat->st_dev,
                  this->stat->st_ino,
                  this->stat->st_mode,
                  this->stat->st_nlink,
                  this->stat->st_uid,
                  this->stat->st_gid,
                  this->stat->st_blksize,
                  this->stat->st_blocks,
                  this->stat->st_size,
                  this->stat->st_atim.tv_sec*1000*1000*1000 + this->stat->st_atim.tv_nsec,
                  this->stat->st_mtim.tv_sec*1000*1000*1000 + this->stat->st_mtim.tv_nsec,
                  this->stat->st_ctim.tv_sec*1000*1000*1000 + this->stat->st_ctim.tv_nsec);

  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->arg1 = 0;
  self->start = 0;
}


/* ===FSTATFS===
 * int fstatfs(int fd, struct statfs *buf);
 *
 */
syscall::fstatfs:entry
/pid != $pid/
{
  self->start = timestamp;
  self->arg0 = arg0;
  self->arg1 = arg1;
}

syscall::fstatfs:return
/self->start && pid != $pid/
{
  this->statfs = (struct statfs*) copyin((uintptr_t) self->arg1, sizeof(struct statfs));
  
  /*
    7196  fstatfs(3, {f_type="EXT2_SUPER_MAGIC", 
                      f_bsize=4096, 
                      f_blocks=4553183, 
                      f_bfree=1919236, 
                      f_bavail=1687940, 
                      f_files=1158720, 
                      f_ffree=658797, 
                      f_fsid={-1853641883, -1823071587}, 
                      f_namelen=255, 
                      f_frsize=4096}) = 0
  */
  printf("%d ", pid);
  printf("%s(%d, {f_type=%d, f_bsize=%d, f_blocks=%d, f_bfree=%d, f_bavail=%d, f_files=%d, f_ffree=%d, f_fsid={%d, %d}, f_namelen=%d, f_frsize=})\t\t ", 
                  probefunc,
                  self->arg0,
                  this->statfs->f_type,
                  this->statfs->f_bsize,
                  this->statfs->f_blocks,
                  this->statfs->f_bfree,
                  this->statfs->f_bavail,
                  this->statfs->f_files,
                  this->statfs->f_ffree,
                  this->statfs->f_fsid.val[0],
                  this->statfs->f_fsid.val[1],
                  this->statfs->f_namemax);
                  /* Note: f_frsize not in bsd statfs struct*/

  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->arg1 = 0;
  self->start = 0;
}



/* ===GETDENTS===
 * int getdents(unsigned int fd, struct linux_dirent *dirp, unsigned int count);
 */
syscall::getdents:entry,
syscall::getdirentries:entry
/pid != $pid/

{
  self->start = timestamp;
  self->arg0 = arg0;
  self->arg1 = arg1;
  self->arg2 = arg2;
}

syscall::getdents:return,
syscall::getdirentries:return

/self->start && pid != $pid/
{
  
  printf("%d ", pid);
  printf("%s(%d, %d)\t\t ", 
                  "getdents", /*Note: renaming of getdirentries to getdents*/
                  self->arg0,
                  self->arg2);

  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->arg1 = 0;
  self->start = 0;
}


/* ===GETSOCKOPT===
 * int getsockopt(int s, int level, int optname, void *optval, int *optlen);
 *
 */
syscall::getsockopt*:entry
/pid != $pid/
{
  self->start = timestamp;
  self->arg0 = arg0;
  self->arg1 = arg1;
  self->arg2 = arg2;
  self->arg3 = arg3;
  self->arg4 = arg4;
}

syscall::getsockopt*:return
/self->start && pid != $pid/
{
  self->len = *(socklen_t *) copyin(self->arg4, sizeof(socklen_t));
  self->val = *(socklen_t *) copyin(self->arg3, self->len);
  
  printf("%d ", pid);
  printf("%s", probefunc);
  printf("(%d, %d, %d, %d, %d)\t\t "
         , self->arg0
         , self->arg1
         , self->arg2
         , self->val
         , self->len);
  
  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->arg1 = 0;
  self->arg2 = 0;
  self->arg3 = 0;
  self->arg4 = 0;
  self->start = 0;
}


/* ===LINK/SYMLINK===
 * int link(const char *existing, const char *new);
 * 
 */
syscall::link*:entry,
syscall::symlink*:entry
/pid != $pid/
{
  self->start = timestamp;
  self->arg0 = arg0;
  self->arg1 = arg1;
}

syscall::link*:return,
syscall::symlink*:return
/self->start && pid != $pid/
{
  printf("%d ", pid);
  printf("%s", probefunc);
  printf("(\"%S\", \"%S\")\t\t "
         , copyinstr(self->arg0)
         , copyinstr(self->arg1));
  
  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->arg1 = 0;
  self->start = 0;
}


/* ===LISTEN/SHUTDOWN===
 * int listen(int sockfd, int backlog);
 * int shutdown(int sockfd, int how);
 */
syscall::listen:entry,
syscall::shutdown:entry
/pid != $pid/

{
  self->start = timestamp;
  self->arg0 = arg0;
  self->arg1 = arg1;
}

syscall::listen:return,
syscall::shutdown:return
/self->start && pid != $pid/
{
  printf("%d ", pid);
  printf("%s", probefunc);
  printf("(%d, %d)\t\t ", 
         self->arg0,
         self->arg1);
  
  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->arg1 = 0;
  self->start = 0;
}


/* ===LSEEK===
 * off_t lseek(int fildes, off_t offset, int whence);
 *
 */
syscall::*lseek:entry
/pid != $pid/
{
  self->start = timestamp;
  self->arg0 = arg0;
  self->arg1 = arg1;
  self->arg2 = arg2;
}

syscall::*lseek:return
/self->start && pid != $pid/
{
  printf("%d ", pid);
  printf("%s", probefunc);
  printf("(%d, %d, %d)\t\t "
         , self->arg0
         , self->arg1
         , self->arg2);
  
  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->arg1 = 0;
  self->arg2 = 0;
  self->start = 0;
}


/* ===OPEN===
 * int open(const char *pathname, int flags, mode_t mode);
 */
syscall::open:entry
/pid != $pid/
{
  self->start = timestamp;
  self->arg0 = arg0;
  self->arg1 = arg1;
  self->arg2 = arg2;
}

syscall::open:return
/self->start && pid != $pid/
{
  printf("%d ", pid);
  printf("%s", probefunc);
  printf("(\"%S\", %d, %d)\t\t ", 
         copyinstr(self->arg0),
         self->arg1,
         self->arg2);
  
  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->arg1 = 0;
  self->arg2 = 0;
  self->start = 0;
}


/* ===READ/WRITE===
 * ssize_t read(int fd, void *buf, size_t count);
 */
syscall::read:entry,
syscall::write:entry
/pid != $pid/

{
  self->start = timestamp;
  self->arg0 = arg0;
  self->arg1 = arg1;
  self->arg2 = arg2;
}

syscall::read:return,
syscall::write:return
/self->start && pid != $pid/
{
  printf("%d ", pid);
  printf("%s", probefunc);
  printf("(%d, \"%s\", %d)\t\t ", 
         self->arg0,
         stringof(copyin(self->arg1, self->arg2)),
         self->arg2);
  
  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->arg1 = 0;
  self->arg2 = 0;
  self->start = 0;
}


/* ===SEND/RECV===
 * ssize_t send(int s, const void *msg, size_t len, int flags);
 * ssize_t recv(int s, void *buf, size_t len, int flags);
 *
 */
syscall::*send:entry,
syscall::*recv:entry
/pid != $pid/
{
  self->start = timestamp;
  self->arg0 = arg0;
  self->arg1 = arg1;
  self->arg2 = arg2;
  self->arg3 = arg3;
}

syscall::*send:return,
syscall::*recv:return
/self->start && pid != $pid/
{
  printf("%d ", pid);
  printf("%s", probefunc);
  printf("(%d, \"%S\", %d, %d)\t\t "
         , self->arg0
         , stringof(copyin(self->arg1, self->arg2))
         , self->arg2
         , self->arg3);
  
  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->arg1 = 0;
  self->arg2 = 0;
  self->arg3 = 0;
  self->start = 0;
}


/* ===RECVFROM===
 * ssize_t recvfrom(int s, void *buf, size_t len, int flags, struct sockaddr *from, socklen_t *fromlen);
 *
 */
syscall::*recvfrom:entry
/pid != $pid/
{
  self->start = timestamp;
  self->arg0 = arg0;
  self->arg1 = arg1;
  self->arg2 = arg2;
  self->arg3 = arg3;
  self->arg4 = arg4;
  self->arg5 = arg5;
}

syscall::*recvfrom:return
/self->start && pid != $pid/
{
  this->sock = (struct sockaddr_in *) copyin(self->arg4, sizeof(struct sockaddr));
  
  self->family = this->sock->sin_family;
  
  self->port = ntohs(this->sock->sin_port);
  
  this->a = (uint8_t *)&this->sock->sin_addr;
  this->addr1 = strjoin(lltostr(this->a[0] + 0ULL), strjoin(".", strjoin(lltostr(this->a[1] + 0ULL), ".")));
  this->addr2 = strjoin(lltostr(this->a[2] + 0ULL), strjoin(".", lltostr(this->a[3] + 0ULL)));
  
  self->ip = strjoin(this->addr1, this->addr2);



  /* self->len = *(socklen_t *) copyin(self->arg5, sizeof(socklen_t)); */


  printf("%d ", pid);
  printf("%s", probefunc);
  printf("(%d, \"%S\", %d, %d,  {sa_family=%d sin_port=htons(%d), sin_addr=inet_addr(\"%s\")}, %d)\t\t "
         , self->arg0
         , stringof(copyin(self->arg1, arg0))
         , self->arg2
         , self->arg3
         , self->family
         , self->port
         , self->ip
         , 0); /*recvfrom fromlen throws an error when tryin to rdereference. see instr in comments above.*/
  
  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->arg1 = 0;
  self->arg2 = 0;
  self->arg3 = 0;
  self->arg4 = 0;
  self->arg5 = 0;
  self->start = 0;
}


/* ===SENDTO===
 * ssize_t sendto(int s, const void *msg, size_t len, int flags, const struct sockaddr *to, int tolen);
 *
 */
syscall::sendto*:entry
/pid != $pid/
{
  self->start = timestamp;
  self->arg0 = arg0;
  self->arg1 = arg1;
  self->arg2 = arg2;
  self->arg3 = arg3;
  
  this->sock = (struct sockaddr_in *) copyin(
                 arg4, sizeof(struct sockaddr));
  self->port = ntohs(this->sock->sin_port);
  this->a = (uint8_t *)&this->sock->sin_addr;
  this->addr1 = strjoin(lltostr(this->a[0] + 0ULL), strjoin(".",
  strjoin(lltostr(this->a[1] + 0ULL), ".")));
  this->addr2 = strjoin(lltostr(this->a[2] + 0ULL), strjoin(".",
  lltostr(this->a[3] + 0ULL)));
  self->ip = strjoin(this->addr1, this->addr2);
  
  self->arg5 = arg5;
}

syscall::sendto*:return
/self->start && pid != $pid/
{
  printf("%d ", pid);
  printf("%s", probefunc);
  printf("(%d, \"%S\", %d, %d,  {sin_port=htons(%d), sin_addr=inet_addr(\"%s\")}, %d)\t\t "
         , self->arg0
         , stringof(copyin(self->arg1, self->arg2))
         , self->arg2
         , self->arg3
         , self->port
         , self->ip
         , self->arg5);
  
  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->arg1 = 0;
  self->arg2 = 0;
  self->arg3 = 0;
  self->arg4 = 0;
  self->arg5 = 0;
  self->start = 0;
}


/* ===SETSOCKOPT===
 * int setsockopt(int s, int level, int optname, const void *optval, int optlen);
 * 
 */
syscall::setsockopt*:entry
/pid != $pid/
{
  self->start = timestamp;
  self->arg0 = arg0;
  self->arg1 = arg1;
  self->arg2 = arg2;
  self->arg3 = arg3;
  self->arg4 = arg4;
}

syscall::setsockopt*:return
/self->start && pid != $pid/
{
  self->val = *(socklen_t *) copyin(self->arg3, self->arg4);
  
  
  printf("%d ", pid);
  printf("%s", probefunc);
  printf("(%d, %d, %d, %d, %d)\t\t "
         , self->arg0
         , self->arg1
         , self->arg2
         , self->val
         , self->arg4);
  
  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->arg1 = 0;
  self->arg2 = 0;
  self->arg3 = 0;
  self->arg4 = 0;
  self->start = 0;
}


/* ===SOCKET===
 * int socket(int domain, int type, int protocol);
 */
syscall::*socket*:entry
/pid != $pid/
{
  self->start = timestamp;
  self->arg0 = arg0;
  self->arg1 = arg1;
  self->arg2 = arg2;
}

syscall::*socket*:return
/self->start && pid != $pid/
{
  printf("%d ", pid);
  printf("%s", "socket");
  printf("(%d, %d, %d)\t\t "
         , self->arg0
         , self->arg1
         , self->arg2);
  
  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->arg1 = 0;
  self->arg2 = 0;
  self->start = 0;
}


/* ===STAT===
 * int stat(const char *path, struct stat *buf);
 *
 */
syscall::stat:entry
/pid != $pid/
{
  self->start = timestamp;
  self->arg0 = arg0;
  self->arg1 = arg1;
}

syscall::stat:return
/self->start && pid != $pid/
{
  this->path = copyinstr(self->arg0);
  
  this->stat = (struct stat*) copyin((uintptr_t) self->arg1, sizeof(struct stat));

  /*
  11433 stat64("syscalls.txt", {st_dev=makedev(8, 6), 
                                st_ino=700117, 
                                st_mode=S_IFREG|0664, 
                                st_nlink=1, 
                                st_uid=1000, 
                                st_gid=1000, 
                                st_blksize=4096, 
                                st_blocks=0, 
                                st_size=0, 
                                st_atime=2013/03/06-04:16:17, 
                                st_mtime=2013/03/06-04:16:17, 
                                st_ctime=2013/03/06-04:16:17}) = 0
  */
  
  printf("%d ", pid);
  printf("%s(%S, {st_dev=%d, st_ino=%d, st_mode=%d, st_nlink=%d, st_uid=%d, st_gid=%d, st_blksize=%d, st_blocks=%d, st_size=%d, st_atime=%d, st_mtime=%d, st_ctime=%d})\t\t ", 
                  probefunc,
                  this->path,
                  this->stat->st_dev,
                  this->stat->st_ino,
                  this->stat->st_mode,
                  this->stat->st_nlink,
                  this->stat->st_uid,
                  this->stat->st_gid,
                  this->stat->st_blksize,
                  this->stat->st_blocks,
                  this->stat->st_size,
                  this->stat->st_atim.tv_sec*1000*1000*1000 + this->stat->st_atim.tv_nsec,
                  this->stat->st_mtim.tv_sec*1000*1000*1000 + this->stat->st_mtim.tv_nsec,
                  this->stat->st_ctim.tv_sec*1000*1000*1000 + this->stat->st_ctim.tv_nsec);

  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->arg1 = 0;
  self->start = 0;
}


/* ===STATFS===
 * int statfs(const char *path, struct statfs *buf);
 */
syscall::statfs:entry
/pid != $pid/
{
  self->start = timestamp;
  self->arg0 = arg0;
  self->arg1 = arg1;
}

syscall::statfs:return
/self->start && pid != $pid/
{
  this->path = copyinstr(self->arg0);

  this->statfs = (struct statfs*) copyin((uintptr_t) self->arg1, sizeof(struct statfs));
  
  printf("%d ", pid);
  printf("%s(%S, {f_type=%d, f_bsize=%d, f_blocks=%d, f_bfree=%d, f_bavail=%d, f_files=%d, f_ffree=%d, f_fsid={%d, %d}, f_namelen=%d, f_frsize=})\t\t ", 
                  probefunc,
                  this->path,
                  this->statfs->f_type,
                  this->statfs->f_bsize,
                  this->statfs->f_blocks,
                  this->statfs->f_bfree,
                  this->statfs->f_bavail,
                  this->statfs->f_files,
                  this->statfs->f_ffree,
                  this->statfs->f_fsid.val[0],
                  this->statfs->f_fsid.val[1],
                  this->statfs->f_namemax);
                  /* Note: f_frsize not in bsd statfs struct*/

  this->errstr = err[errno] != NULL ? err[errno] : "";
  printf("= %d %s\n", (int) arg0, this->errstr);
  
  self->arg0 = 0;
  self->arg1 = 0;
  self->start = 0;
}


/* program exited */
proc:::exit
/pid == $target/
{
	exit(0);
}

dtrace:::END
{
}
/*
 * Author Savvas Savvides
 * Date 12-12-12
 * 
 * Run system calls
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "syscalls_functions.h"

#define NOT_IMPL 0
#define IMPLEMEN 1

typedef struct {
  char* name;
  int (*f)();
  unsigned char implemented;
} SysCalls;

const SysCalls SYSCALLS[] = {
  {"accept",                 execute_accept,                 IMPLEMEN},
  {"accept4",                execute_accept4,                NOT_IMPL},
  {"access",                 execute_access,                 IMPLEMEN},
  {"acct",                   execute_acct,                   NOT_IMPL},
  {"add_key",                execute_add_key,                NOT_IMPL},
  {"adjtimex",               execute_adjtimex,               NOT_IMPL},
  {"afs_syscall",            execute_afs_syscall,            NOT_IMPL},
  {"alarm",                  execute_alarm,                  NOT_IMPL},
  {"alloc_hugepages",        execute_alloc_hugepages,        NOT_IMPL},
  {"bdflush",                execute_bdflush,                NOT_IMPL},
  {"bind",                   execute_bind,                   IMPLEMEN},
  {"break",                  execute_break,                  NOT_IMPL},
  {"brk",                    execute_brk,                    NOT_IMPL},
  {"cacheflush",             execute_cacheflush,             NOT_IMPL},
  {"capget",                 execute_capget,                 NOT_IMPL},
  {"capset",                 execute_capset,                 NOT_IMPL},
  {"chdir",                  execute_chdir,                  IMPLEMEN},
  {"chmod",                  execute_chmod,                  NOT_IMPL},
  {"chown",                  execute_chown,                  NOT_IMPL},
  {"chown32",                execute_chown32,                NOT_IMPL},
  {"chroot",                 execute_chroot,                 NOT_IMPL},
  {"clock_getres",           execute_clock_getres,           NOT_IMPL},
  {"clock_gettime",          execute_clock_gettime,          NOT_IMPL},
  {"clock_nanosleep",        execute_clock_nanosleep,        NOT_IMPL},
  {"clock_settime",          execute_clock_settime,          NOT_IMPL},
  {"clone",                  execute_clone,                  NOT_IMPL},
  {"close",                  execute_close,                  IMPLEMEN},
  {"connect",                execute_connect,                IMPLEMEN},
  {"creat",                  execute_creat,                  IMPLEMEN},
  {"create_module",          execute_create_module,          NOT_IMPL},
  {"delete_module",          execute_delete_module,          NOT_IMPL},
  {"dup",                    execute_dup,                    IMPLEMEN},
  {"dup2",                   execute_dup2,                   IMPLEMEN},
  {"dup3",                   execute_dup3,                   IMPLEMEN},
  {"epoll_create",           execute_epoll_create,           NOT_IMPL},
  {"epoll_create1",          execute_epoll_create1,          NOT_IMPL},
  {"epoll_ctl",              execute_epoll_ctl,              NOT_IMPL},
  {"epoll_pwait",            execute_epoll_pwait,            NOT_IMPL},
  {"epoll_wait",             execute_epoll_wait,             NOT_IMPL},
  {"eventfd",                execute_eventfd,                NOT_IMPL},
  {"eventfd2",               execute_eventfd2,               NOT_IMPL},
  {"execve",                 execute_execve,                 NOT_IMPL},
  {"exit",                   execute_exit,                   NOT_IMPL},
  {"exit_group",             execute_exit_group,             NOT_IMPL},
  {"faccessat",              execute_faccessat,              NOT_IMPL},
  {"fadvise64",              execute_fadvise64,              NOT_IMPL},
  {"fadvise64_64",           execute_fadvise64_64,           NOT_IMPL},
  {"fallocate",              execute_fallocate,              NOT_IMPL},
  {"fchdir",                 execute_fchdir,                 IMPLEMEN},
  {"fchmod",                 execute_fchmod,                 NOT_IMPL},
  {"fchmodat",               execute_fchmodat,               NOT_IMPL},
  {"fchown",                 execute_fchown,                 NOT_IMPL},
  {"fchown32",               execute_fchown32,               NOT_IMPL},
  {"fchownat",               execute_fchownat,               NOT_IMPL},
  {"fcntl",                  execute_fcntl,                  IMPLEMEN},
  {"fcntl64",                execute_fcntl64,                NOT_IMPL},
  {"fdatasync",              execute_fdatasync,              NOT_IMPL},
  {"fgetxattr",              execute_fgetxattr,              NOT_IMPL},
  {"flistxattr",             execute_flistxattr,             NOT_IMPL},
  {"flock",                  execute_flock,                  NOT_IMPL},
  {"fork",                   execute_fork,                   NOT_IMPL},
  {"free_hugepages",         execute_free_hugepages,         NOT_IMPL},
  {"fremovexattr",           execute_fremovexattr,           NOT_IMPL},
  {"fsetxattr",              execute_fsetxattr,              NOT_IMPL},
  {"fstat",                  execute_fstat,                  IMPLEMEN},
  {"fstat64",                execute_fstat64,                NOT_IMPL},
  {"fstatat64",              execute_fstatat64,              NOT_IMPL},
  {"fstatvfs",                execute_fstatvfs,               IMPLEMEN},
  {"fstatvfs64",              execute_fstatvfs64,             NOT_IMPL},
  {"fsync",                  execute_fsync,                  NOT_IMPL},
  {"ftime",                  execute_ftime,                  NOT_IMPL},
  {"ftruncate",              execute_ftruncate,              NOT_IMPL},
  {"ftruncate64",            execute_ftruncate64,            NOT_IMPL},
  {"futex",                  execute_futex,                  NOT_IMPL},
  {"futimesat",              execute_futimesat,              NOT_IMPL},
  {"get_kernel_syms",        execute_get_kernel_syms,        NOT_IMPL},
  {"get_mempolicy",          execute_get_mempolicy,          NOT_IMPL},
  {"get_robust_list",        execute_get_robust_list,        NOT_IMPL},
  {"get_thread_area",        execute_get_thread_area,        NOT_IMPL},
  {"getcpu",                 execute_getcpu,                 NOT_IMPL},
  {"getcwd",                 execute_getcwd,                 NOT_IMPL},
  {"getdents",               execute_getdents,               IMPLEMEN},
  {"getdents64",             execute_getdents64,             NOT_IMPL},
  {"getegid",                execute_getegid,                NOT_IMPL},
  {"getegid32",              execute_getegid32,              NOT_IMPL},
  {"geteuid",                execute_geteuid,                NOT_IMPL},
  {"geteuid32",              execute_geteuid32,              NOT_IMPL},
  {"getgid",                 execute_getgid,                 NOT_IMPL},
  {"getgid32",               execute_getgid32,               NOT_IMPL},
  {"getgroups",              execute_getgroups,              NOT_IMPL},
  {"getgroups32",            execute_getgroups32,            NOT_IMPL},
  {"getitimer",              execute_getitimer,              NOT_IMPL},
  {"getpeername",            execute_getpeername,            IMPLEMEN},
  {"getpagesize",            execute_getpagesize,            NOT_IMPL},
  {"getpgid",                execute_getpgid,                NOT_IMPL},
  {"getpgrp",                execute_getpgrp,                NOT_IMPL},
  {"getpid",                 execute_getpid,                 NOT_IMPL},
  {"getpmsg",                execute_getpmsg,                NOT_IMPL},
  {"getppid",                execute_getppid,                NOT_IMPL},
  {"getpriority",            execute_getpriority,            NOT_IMPL},
  {"getresgid",              execute_getresgid,              NOT_IMPL},
  {"getresgid32",            execute_getresgid32,            NOT_IMPL},
  {"getresuid",              execute_getresuid,              NOT_IMPL},
  {"getresuid32",            execute_getresuid32,            NOT_IMPL},
  {"getrlimit",              execute_getrlimit,              NOT_IMPL},
  {"getrusage",              execute_getrusage,              NOT_IMPL},
  {"getsid",                 execute_getsid,                 NOT_IMPL},
  {"getsockname",            execute_getsockname,            IMPLEMEN},
  {"getsockopt",             execute_getsockopt,             IMPLEMEN},
  {"gettid",                 execute_gettid,                 NOT_IMPL},
  {"gettimeofday",           execute_gettimeofday,           NOT_IMPL},
  {"getuid",                 execute_getuid,                 NOT_IMPL},
  {"getuid32",               execute_getuid32,               NOT_IMPL},
  {"getxattr",               execute_getxattr,               NOT_IMPL},
  {"gtty",                   execute_gtty,                   NOT_IMPL},
  {"idle",                   execute_idle,                   NOT_IMPL},
  {"init_module",            execute_init_module,            NOT_IMPL},
  {"inotify_add_watch",      execute_inotify_add_watch,      NOT_IMPL},
  {"inotify_init",           execute_inotify_init,           NOT_IMPL},
  {"inotify_init1",          execute_inotify_init1,          NOT_IMPL},
  {"inotify_rm_watch",       execute_inotify_rm_watch,       NOT_IMPL},
  {"io_cancel",              execute_io_cancel,              NOT_IMPL},
  {"io_destroy",             execute_io_destroy,             NOT_IMPL},
  {"io_getevents",           execute_io_getevents,           NOT_IMPL},
  {"io_setup",               execute_io_setup,               NOT_IMPL},
  {"io_submit",              execute_io_submit,              NOT_IMPL},
  {"ioctl",                  execute_ioctl,                  NOT_IMPL},
  {"ioperm",                 execute_ioperm,                 NOT_IMPL},
  {"iopl",                   execute_iopl,                   NOT_IMPL},
  {"ioprio_get",             execute_ioprio_get,             NOT_IMPL},
  {"ioprio_set",             execute_ioprio_set,             NOT_IMPL},
  {"ipc",                    execute_ipc,                    NOT_IMPL},
  {"kexec_load",             execute_kexec_load,             NOT_IMPL},
  {"keyctl",                 execute_keyctl,                 NOT_IMPL},
  {"kill",                   execute_kill,                   NOT_IMPL},
  {"lchown",                 execute_lchown,                 NOT_IMPL},
  {"lchown32",               execute_lchown32,               NOT_IMPL},
  {"lgetxattr",              execute_lgetxattr,              NOT_IMPL},
  {"link",                   execute_link,                   IMPLEMEN},
  {"linkat",                 execute_linkat,                 NOT_IMPL},
  {"listen",                 execute_listen,                 IMPLEMEN},
  {"listxattr",              execute_listxattr,              NOT_IMPL},
  {"llistxattr",             execute_llistxattr,             NOT_IMPL},
  {"lock",                   execute_lock,                   NOT_IMPL},
  {"lookup_dcookie",         execute_lookup_dcookie,         NOT_IMPL},
  {"lremovexattr",           execute_lremovexattr,           NOT_IMPL},
  {"lseek",                  execute_lseek,                  IMPLEMEN},
  {"lsetxattr",              execute_lsetxattr,              NOT_IMPL},
  {"lstat",                  execute_lstat,                  IMPLEMEN},
  {"lstat64",                execute_lstat64,                NOT_IMPL},
  {"madvise",                execute_madvise,                NOT_IMPL},
  {"madvise1",               execute_madvise1,               NOT_IMPL},
  {"mbind",                  execute_mbind,                  NOT_IMPL},
  {"migrate_pages",          execute_migrate_pages,          NOT_IMPL},
  {"mincore",                execute_mincore,                NOT_IMPL},
  {"mkdir",                  execute_mkdir,                  IMPLEMEN},
  {"mkdirat",                execute_mkdirat,                NOT_IMPL},
  {"mknod",                  execute_mknod,                  NOT_IMPL},
  {"mknodat",                execute_mknodat,                NOT_IMPL},
  {"mlock",                  execute_mlock,                  NOT_IMPL},
  {"mlockall",               execute_mlockall,               NOT_IMPL},
  {"mmap",                   execute_mmap,                   NOT_IMPL},
  {"mmap2",                  execute_mmap2,                  NOT_IMPL},
  {"modify_ldt",             execute_modify_ldt,             NOT_IMPL},
  {"mount",                  execute_mount,                  NOT_IMPL},
  {"move_pages",             execute_move_pages,             NOT_IMPL},
  {"mprotect",               execute_mprotect,               NOT_IMPL},
  {"mpx",                    execute_mpx,                    NOT_IMPL},
  {"mq_getsetattr",          execute_mq_getsetattr,          NOT_IMPL},
  {"mq_notify",              execute_mq_notify,              NOT_IMPL},
  {"mq_open",                execute_mq_open,                NOT_IMPL},
  {"mq_timedreceive",        execute_mq_timedreceive,        NOT_IMPL},
  {"mq_timedsend",           execute_mq_timedsend,           NOT_IMPL},
  {"mq_unlink",              execute_mq_unlink,              NOT_IMPL},
  {"mremap",                 execute_mremap,                 NOT_IMPL},
  {"msgctl",                 execute_msgctl,                 NOT_IMPL},
  {"msgget",                 execute_msgget,                 NOT_IMPL},
  {"msgrcv",                 execute_msgrcv,                 NOT_IMPL},
  {"msgsnd",                 execute_msgsnd,                 NOT_IMPL},
  {"msync",                  execute_msync,                  NOT_IMPL},
  {"munlock",                execute_munlock,                NOT_IMPL},
  {"munlockall",             execute_munlockall,             NOT_IMPL},
  {"munmap",                 execute_munmap,                 NOT_IMPL},
  {"nanosleep",              execute_nanosleep,              NOT_IMPL},
  {"nfsservctl",             execute_nfsservctl,             NOT_IMPL},
  {"nice",                   execute_nice,                   NOT_IMPL},
  {"oldfstat",               execute_oldfstat,               NOT_IMPL},
  {"oldlstat",               execute_oldlstat,               NOT_IMPL},
  {"oldolduname",            execute_oldolduname,            NOT_IMPL},
  {"oldstat",                execute_oldstat,                NOT_IMPL},
  {"olduname",               execute_olduname,               NOT_IMPL},
  {"open",                   execute_open,                   IMPLEMEN},
  {"openat",                 execute_openat,                 NOT_IMPL},
  {"pause",                  execute_pause,                  NOT_IMPL},
  {"pciconfig_iobase",       execute_pciconfig_iobase,       NOT_IMPL},
  {"pciconfig_read",         execute_pciconfig_read,         NOT_IMPL},
  {"pciconfig_write",        execute_pciconfig_write,        NOT_IMPL},
  {"perf_event_open",        execute_perf_event_open,        NOT_IMPL},
  {"personality",            execute_personality,            NOT_IMPL},
  {"phys",                   execute_phys,                   NOT_IMPL},
  {"pipe",                   execute_pipe,                   NOT_IMPL},
  {"pipe2",                  execute_pipe2,                  NOT_IMPL},
  {"pivot_root",             execute_pivot_root,             NOT_IMPL},
  {"poll",                   execute_poll,                   NOT_IMPL},
  {"ppoll",                  execute_ppoll,                  NOT_IMPL},
  {"prctl",                  execute_prctl,                  NOT_IMPL},
  {"pread64",                execute_pread64,                NOT_IMPL},
  {"preadv",                 execute_preadv,                 NOT_IMPL},
  {"prlimit",                execute_prlimit,                NOT_IMPL},
  {"prof",                   execute_prof,                   NOT_IMPL},
  {"profil",                 execute_profil,                 NOT_IMPL},
  {"pselect6",               execute_pselect6,               NOT_IMPL},
  {"ptrace",                 execute_ptrace,                 NOT_IMPL},
  {"putpmsg",                execute_putpmsg,                NOT_IMPL},
  {"pwrite64",               execute_pwrite64,               NOT_IMPL},
  {"pwritev",                execute_pwritev,                NOT_IMPL},
  {"query_module",           execute_query_module,           NOT_IMPL},
  {"quotactl",               execute_quotactl,               NOT_IMPL},
  {"read",                   execute_read,                   IMPLEMEN},
  {"readahead",              execute_readahead,              NOT_IMPL},
  {"readdir",                execute_readdir,                NOT_IMPL},
  {"readlink",               execute_readlink,               NOT_IMPL},
  {"readlinkat",             execute_readlinkat,             NOT_IMPL},
  {"readv",                  execute_readv,                  NOT_IMPL},
  {"reboot",                 execute_reboot,                 NOT_IMPL},
  {"recv",                   execute_recv,                   IMPLEMEN},
  {"recvfrom",               execute_recvfrom,               IMPLEMEN},
  {"recvmsg",                execute_recvmsg,                NOT_IMPL},
  {"recvmmsg",               execute_recvmmsg,               NOT_IMPL},
  {"remap_file_pages",       execute_remap_file_pages,       NOT_IMPL},
  {"removexattr",            execute_removexattr,            NOT_IMPL},
  {"rename",                 execute_rename,                 NOT_IMPL},
  {"renameat",               execute_renameat,               NOT_IMPL},
  {"request_key",            execute_request_key,            NOT_IMPL},
  {"restart_syscall",        execute_restart_syscall,        NOT_IMPL},
  {"rmdir",                  execute_rmdir,                  IMPLEMEN},
  {"rt_sigaction",           execute_rt_sigaction,           NOT_IMPL},
  {"rt_sigpending",          execute_rt_sigpending,          NOT_IMPL},
  {"rt_sigprocmask",         execute_rt_sigprocmask,         NOT_IMPL},
  {"rt_sigqueueinfo",        execute_rt_sigqueueinfo,        NOT_IMPL},
  {"rt_sigreturn",           execute_rt_sigreturn,           NOT_IMPL},
  {"rt_sigsuspend",          execute_rt_sigsuspend,          NOT_IMPL},
  {"rt_sigtimedwait",        execute_rt_sigtimedwait,        NOT_IMPL},
  {"rt_tgsigqueueinfo",      execute_rt_tgsigqueueinfo,      NOT_IMPL},
  {"sched_get_priority_max", execute_sched_get_priority_max, NOT_IMPL},
  {"sched_get_priority_min", execute_sched_get_priority_min, NOT_IMPL},
  {"sched_getaffinity",      execute_sched_getaffinity,      NOT_IMPL},
  {"sched_getparam",         execute_sched_getparam,         NOT_IMPL},
  {"sched_getscheduler",     execute_sched_getscheduler,     NOT_IMPL},
  {"sched_rr_get_interval",  execute_sched_rr_get_interval,  NOT_IMPL},
  {"sched_setaffinity",      execute_sched_setaffinity,      NOT_IMPL},
  {"sched_setparam",         execute_sched_setparam,         NOT_IMPL},
  {"sched_setscheduler",     execute_sched_setscheduler,     NOT_IMPL},
  {"sched_yield",            execute_sched_yield,            NOT_IMPL},
  {"security",               execute_security,               NOT_IMPL},
  {"select",                 execute_select,                 NOT_IMPL},
  {"semctl",                 execute_semctl,                 NOT_IMPL},
  {"semget",                 execute_semget,                 NOT_IMPL},
  {"semop",                  execute_semop,                  NOT_IMPL},
  {"semtimedop",             execute_semtimedop,             NOT_IMPL},
  {"send",                   execute_send,                   IMPLEMEN},
  {"sendfile",               execute_sendfile,               NOT_IMPL},
  {"sendfile64",             execute_sendfile64,             NOT_IMPL},
  {"sendmsg",                execute_sendmsg,                IMPLEMEN},
  {"sendto",                 execute_sendto,                 IMPLEMEN},
  {"set_mempolicy",          execute_set_mempolicy,          NOT_IMPL},
  {"set_robust_list",        execute_set_robust_list,        NOT_IMPL},
  {"set_thread_area",        execute_set_thread_area,        NOT_IMPL},
  {"set_tid_address",        execute_set_tid_address,        NOT_IMPL},
  {"set_zone_reclaim",       execute_set_zone_reclaim,       NOT_IMPL},
  {"setdomainname",          execute_setdomainname,          NOT_IMPL},
  {"setfsgid",               execute_setfsgid,               NOT_IMPL},
  {"setfsgid32",             execute_setfsgid32,             NOT_IMPL},
  {"setfsuid",               execute_setfsuid,               NOT_IMPL},
  {"setfsuid32",             execute_setfsuid32,             NOT_IMPL},
  {"setgid",                 execute_setgid,                 NOT_IMPL},
  {"setgid32",               execute_setgid32,               NOT_IMPL},
  {"setgroups",              execute_setgroups,              NOT_IMPL},
  {"setgroups32",            execute_setgroups32,            NOT_IMPL},
  {"sethostname",            execute_sethostname,            NOT_IMPL},
  {"setitimer",              execute_setitimer,              NOT_IMPL},
  {"setpgid",                execute_setpgid,                NOT_IMPL},
  {"setpriority",            execute_setpriority,            NOT_IMPL},
  {"setregid",               execute_setregid,               NOT_IMPL},
  {"setregid32",             execute_setregid32,             NOT_IMPL},
  {"setresgid",              execute_setresgid,              NOT_IMPL},
  {"setresgid32",            execute_setresgid32,            NOT_IMPL},
  {"setresuid",              execute_setresuid,              NOT_IMPL},
  {"setresuid32",            execute_setresuid32,            NOT_IMPL},
  {"setreuid",               execute_setreuid,               NOT_IMPL},
  {"setreuid32",             execute_setreuid32,             NOT_IMPL},
  {"setrlimit",              execute_setrlimit,              NOT_IMPL},
  {"setsid",                 execute_setsid,                 NOT_IMPL},
  {"setsockopt",             execute_setsockopt,             IMPLEMEN},
  {"settimeofday",           execute_settimeofday,           NOT_IMPL},
  {"setuid",                 execute_setuid,                 NOT_IMPL},
  {"setuid32",               execute_setuid32,               NOT_IMPL},
  {"setup",                  execute_setup,                  NOT_IMPL},
  {"setxattr",               execute_setxattr,               NOT_IMPL},
  {"sgetmask",               execute_sgetmask,               NOT_IMPL},
  {"shmat",                  execute_shmat,                  NOT_IMPL},
  {"shmctl",                 execute_shmctl,                 NOT_IMPL},
  {"shmdt",                  execute_shmdt,                  NOT_IMPL},
  {"shmget",                 execute_shmget,                 NOT_IMPL},
  {"shutdown",               execute_shutdown,               IMPLEMEN},
  {"sigaction",              execute_sigaction,              NOT_IMPL},
  {"sigaltstack",            execute_sigaltstack,            NOT_IMPL},
  {"signal",                 execute_signal,                 NOT_IMPL},
  {"signalfd",               execute_signalfd,               NOT_IMPL},
  {"signalfd4",              execute_signalfd4,              NOT_IMPL},
  {"sigpending",             execute_sigpending,             NOT_IMPL},
  {"sigprocmask",            execute_sigprocmask,            NOT_IMPL},
  {"sigreturn",              execute_sigreturn,              NOT_IMPL},
  {"sigsuspend",             execute_sigsuspend,             NOT_IMPL},
  {"socket",                 execute_socket,                 IMPLEMEN},
  {"socketcall",             execute_socketcall,             NOT_IMPL},
  {"socketpair",             execute_socketpair,             NOT_IMPL},
  {"splice",                 execute_splice,                 NOT_IMPL},
  {"spu_create",             execute_spu_create,             NOT_IMPL},
  {"spu_run",                execute_spu_run,                NOT_IMPL},
  {"ssetmask",               execute_ssetmask,               NOT_IMPL},
  {"stat",                   execute_stat,                   IMPLEMEN},
  {"stat64",                 execute_stat64,                 NOT_IMPL},
  {"statvfs",                execute_statvfs,                IMPLEMEN},
  {"statvfs64",              execute_statvfs64,              NOT_IMPL},
  {"stime",                  execute_stime,                  NOT_IMPL},
  {"stty",                   execute_stty,                   NOT_IMPL},
  {"subpage_prot",           execute_subpage_prot,           NOT_IMPL},
  {"swapoff",                execute_swapoff,                NOT_IMPL},
  {"swapon",                 execute_swapon,                 NOT_IMPL},
  {"symlink",                execute_symlink,                IMPLEMEN},
  {"symlinkat",              execute_symlinkat,              NOT_IMPL},
  {"sync",                   execute_sync,                   NOT_IMPL},
  {"sync_file_range",        execute_sync_file_range,        NOT_IMPL},
  {"sync_file_range2",       execute_sync_file_range2,       NOT_IMPL},
  {"sysfs",                  execute_sysfs,                  NOT_IMPL},
  {"sysinfo",                execute_sysinfo,                NOT_IMPL},
  {"syslog",                 execute_syslog,                 NOT_IMPL},
  {"tee",                    execute_tee,                    NOT_IMPL},
  {"tgkill",                 execute_tgkill,                 NOT_IMPL},
  {"time",                   execute_time,                   NOT_IMPL},
  {"timer_create",           execute_timer_create,           NOT_IMPL},
  {"timer_delete",           execute_timer_delete,           NOT_IMPL},
  {"timer_getoverrun",       execute_timer_getoverrun,       NOT_IMPL},
  {"timer_gettime",          execute_timer_gettime,          NOT_IMPL},
  {"timer_settime",          execute_timer_settime,          NOT_IMPL},
  {"timerfd_create",         execute_timerfd_create,         NOT_IMPL},
  {"timerfd_gettime",        execute_timerfd_gettime,        NOT_IMPL},
  {"timerfd_settime",        execute_timerfd_settime,        NOT_IMPL},
  {"times",                  execute_times,                  NOT_IMPL},
  {"tkill",                  execute_tkill,                  NOT_IMPL},
  {"truncate",               execute_truncate,               NOT_IMPL},
  {"truncate64",             execute_truncate64,             NOT_IMPL},
  {"tuxcall",                execute_tuxcall,                NOT_IMPL},
  {"ugetrlimit",             execute_ugetrlimit,             NOT_IMPL},
  {"ulimit",                 execute_ulimit,                 NOT_IMPL},
  {"umask",                  execute_umask,                  NOT_IMPL},
  {"umount",                 execute_umount,                 NOT_IMPL},
  {"umount2",                execute_umount2,                NOT_IMPL},
  {"uname",                  execute_uname,                  NOT_IMPL},
  {"unlink",                 execute_unlink,                 IMPLEMEN},
  {"unlinkat",               execute_unlinkat,               NOT_IMPL},
  {"unshare",                execute_unshare,                NOT_IMPL},
  {"uselib",                 execute_uselib,                 NOT_IMPL},
  {"ustat",                  execute_ustat,                  NOT_IMPL},
  {"utime",                  execute_utime,                  NOT_IMPL},
  {"utimensat",              execute_utimensat,              NOT_IMPL},
  {"utimes",                 execute_utimes,                 NOT_IMPL},
  {"vfork",                  execute_vfork,                  NOT_IMPL},
  {"vhangup",                execute_vhangup,                NOT_IMPL},
  {"vm86old",                execute_vm86old,                NOT_IMPL},
  {"vmsplice",               execute_vmsplice,               NOT_IMPL},
  {"vserver",                execute_vserver,                NOT_IMPL},
  {"wait4",                  execute_wait4,                  NOT_IMPL},
  {"waitid",                 execute_waitid,                 NOT_IMPL},
  {"waitpid",                execute_waitpid,                NOT_IMPL},
  {"write",                  execute_write,                  IMPLEMEN},
  {"writev",                 execute_writev,                 0}
};
const unsigned short SYSCALLS_LENGTH 
                     = sizeof(SYSCALLS)/sizeof(SYSCALLS[0]);


/*
 * This function lists system calls in stdout.
 * 
 */
void list_syscalls(char* choice) {
  int i, implemented = 0;  
  if(strcmp(choice, "implemented") == 0) {
    fprintf(stdout, "Implemented System Calls\n");
    for(i=0; i<SYSCALLS_LENGTH; i++)
      if(SYSCALLS[i].implemented == 1)
        fprintf(stdout, "%3d: %s\n", ++implemented, SYSCALLS[i].name);
    fprintf(stdout, "\n %d out of %d system calls implemented.\n"
                    , implemented, SYSCALLS_LENGTH);
    return;
  }
  
  for(i=0; i<SYSCALLS_LENGTH; i++)
    if(strcmp(choice, SYSCALLS[i].name) == 0) {
      fprintf(stdout, "`%s' system call is %simplemented.\n"
        , SYSCALLS[i].name, SYSCALLS[i].implemented == 1 ? "" : "not ");
      return;
    }
  
  // list all
  implemented = 0;
  for(i=0; i<SYSCALLS_LENGTH; i++) {
    if(SYSCALLS[i].implemented == 1) implemented++;
    fprintf(stdout, "%22s: %s\n", SYSCALLS[i].name,
            SYSCALLS[i].implemented == 1 ? 
            "implemented" : "not implemented");
  }
  fprintf(stdout, "\n %d out of %d system calls implemented.\n"
                  , implemented, SYSCALLS_LENGTH);
} // list_syscalls

/*
 * This function produces a usage help message.
 * 
 * 
 */
void usage_help(char *argv[]) {
  fprintf(stdout, "Usage help...\n");
} // usage_help


/*
 * This function checks if the given comamnd line arguments are
 * valid and decides which system calls are to be executed.
 *
 */
int validate_arguments(int argc, char *argv[]) {
  if(argc < 2) {
    // if no command line arguments are given
    // print a message and exit.
    fprintf(stderr, "%s: missing arguments\n", argv[0]);
    fprintf(stderr, "Try `%s --help' for more information\n", argv[0]);
    exit(EXIT_FAILURE);
  }
  else if(strcmp(argv[1], "--help") == 0) {
    // if the first command line argument is "--help"
    // print usage help.
    usage_help(argv);
    exit(EXIT_SUCCESS);
  }
  else if(strcmp(argv[1], "all") == 0) {
    // if the first command line argument is "all"
    // all system calls must be run.
    return -1;
  }
  else if(strcmp(argv[1], "list") == 0) {
    // if the first command line argument is "list"
    // system calls dealt with must be listed
    return -2;
  }
  else {
    // check if the first command line argument matches one of the 
    // system calls.
    int i;
    for(i=0; i<SYSCALLS_LENGTH; i++)
      if(strcmp(argv[1], SYSCALLS[i].name) == 0)
        return i;
    
    // if no command line arguments are given
    // print a message and exit.
    fprintf(stderr, "%s: invalid option -- '%s'\n", argv[0], argv[1]);
    fprintf(stderr, "Try `%s --help' for more information\n", argv[0]);
    exit(EXIT_FAILURE);
  }
} // validate_arguments


int main(int argc, char *argv[]) {
	int syscall_choice = validate_arguments(argc, argv);
	int i, count=0;
	if(syscall_choice == -1) { // ALL
	  for(i=0; i<SYSCALLS_LENGTH; i++)
	    if(SYSCALLS[i].implemented == 1) {
        SYSCALLS[i].f();
        fprintf(stdout, "%3d: %s\n", ++count, SYSCALLS[i].name);
      }
	}
	else if(syscall_choice == -2) { // LIST
	  if(argc > 2) list_syscalls(argv[2]);
	  else list_syscalls("all");
	}
	else if(syscall_choice >= 0 && syscall_choice < SYSCALLS_LENGTH)
	  if(SYSCALLS[syscall_choice].implemented == 1)
	    SYSCALLS[syscall_choice].f();
	  else {
	    fprintf(stderr, "%s: System call `%s' not implemented.\n"
	                    , argv[0], SYSCALLS[syscall_choice].name);
      fprintf(stderr, "Try `%s list implemented' to see a list of "
                      "system calls implemented.\n", argv[0]);
      exit(EXIT_FAILURE);
	  }
	else {
	  fprintf(stderr, "%s: Unexpected case occured.\n", argv[0]);
    fprintf(stderr, "Try `%s --help' for more information\n", argv[0]);
    exit(EXIT_FAILURE);
	}
  
  return 0;
}

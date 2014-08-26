#ifndef CHECKAPICOMMON_H_
#define CHECKAPICOMMON_H_

// Must parallel defines in aprtrace.h and framework.checkapi_globals.py
#define NULLINT -9999

// Python oracle and fs functions
int (*oracle_get_id)(void);
int (*oracle_getter)(int, char*);
int (*fs_setfsflags)(int, int);
int (*fs_getfsflags)(int);
int (*fs_addfsflags)(int, int);
int (*fs_setcloexec)(int, int);
//int (*fs_fcntl2)(int, int);
//int (*fs_fcntl3)(int, int, int);
int (*fs_dup2)(int, int);
int (*fs_dup)(int);
int (*fs_open)(char*, int, int);
int (*fs_close)(int);
int (*fs_unlink)(char*);
void (*set_errno)(int);
int (*get_errno)(void);

/*
 * Get python functions
 */
void set_py_functions(int (oracle_get_id_)(void),
                      int (oracle_getter_)(int, char*),
                      int (fs_setfsflags_)(int, int),
                      int (fs_getfsflags_)(int),
                      int (fs_addfsflags_)(int, int),
                      int (fs_setcloexec_)(int, int),
                      //int (fs_fcntl2_)(int, int),
                      //int (fs_fcntl3_)(int, int, int),
                      int (fs_dup_)(int),
                      int (fs_dup2_)(int, int),
                      int (fs_open_)(char*, int, int),
                      int (fs_close_)(int),
                      int (fs_unlink_)(char*),
                      void (*set_errno_)(int),
                      int (*get_errno_)(void));

#endif

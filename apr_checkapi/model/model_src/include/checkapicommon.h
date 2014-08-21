#ifndef CHECKAPICOMMON_H_
#define CHECKAPICOMMON_H_

// Must parallel defines in ../tracing/aprtrace.h
#define NULLINT -9999

// Python oracle and fs functions
int (*oracle_get_id)(void);
int (*oracle_getter)(int, char*);
int (*fs_fcntl2)(int, int);
int (*fs_fcntl3)(int, int, int);
int (*fs_open)(char*, int, int);
int (*fs_unlink)(char*);
void (*set_errno)(int);
int (*get_errno)(void);

/*
 * Get python functions
 */
void set_py_functions(int (oracle_get_id_)(void),
                      int (oracle_getter_)(int, char*),
                      int (fs_fcntl2_)(int, int),
                      int (fs_fcntl3_)(int, int, int),
                      int (fs_open_)(char*, int, int),
                      int (fs_unlink_)(char*),
                      void (*set_errno)(int),
                      int (*get_errno)(void));

#endif

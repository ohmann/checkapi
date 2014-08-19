#ifndef CHECKAPICOMMON_H_
#define CHECKAPICOMMON_H_

// Python oracle and fs functions
int (*oracle_get_id)(void);
int (*oracle_getter)(int, char*);
int (*fs_open)(char*, int);
int (*fs_unlink)(char*);

/*
 * Get python functions
 */
void set_py_functions_common(int (oracle_get_id_)(void),
                      int (oracle_getter_)(int, char*),
                      int (fs_open_)(char*, int),
                      int (fs_unlink_)(char*));

#endif

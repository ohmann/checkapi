#include "checkapicommon.h"

/*
 * Get python functions
 */
void set_py_functions_common(int (oracle_get_id_)(void),
                      int (oracle_getter_)(int, char*),
                      int (fs_open_)(char*, int),
                      int (fs_unlink_)(char*)) {
  oracle_get_id = oracle_get_id_;
  oracle_getter = oracle_getter_;
  fs_open = fs_open_;
  fs_unlink = fs_unlink_;
}

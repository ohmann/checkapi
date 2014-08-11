#include <stdio.h>
#include <fcntl.h>

// Previously retrieved random ints
int previous[64];
int prev_index = 0;

// Python oracle and fs functions
int (*oracle_get_id)(void);
int (*oracle_getter)(int, char*);
int (*fs_open)(char*, int);
int (*fs_unlink)(char*);

/*
 * Get python functions
 */
void set_py_functions(int (oracle_get_id_)(void),
                      int (oracle_getter_)(int, char*),
                      int (fs_open_)(char*, int),
                      int (fs_unlink_)(char*)) {
  oracle_get_id = oracle_get_id_;
  oracle_getter = oracle_getter_;
  fs_open = fs_open_;
  fs_unlink = fs_unlink_;
}

/*
 * Returns a random int between 0-255
 */
int get_new_random() {
  // Get id for oracle data
  int oracle_id = (*oracle_get_id)();

  // Get random int
  int num = (*oracle_getter)(oracle_id, "^<RANGE 0, 255>$");

  // Store random int for later calls to get_prior_random(), and return
  previous[prev_index++] = num;
  return num;
}

/*
 * Returns a previously retrieved random int. If index is negative, returns -1.
 * If index is >= the number of random ints previously retrieved, returns -2.
 */
int get_prior_random(int index) {
  // Negative index
  if (index < 0) {
    return -1;
  // Index out of bounds
  } else if (index >= prev_index) {
    return -2;
  }

  return previous[index];
}

/*
 * Opens a file, placing the file descriptor in fd. On success, returns 0. On
 * failure, returns -1.
 */
int file_open(int *fd, char *filename, int flags) {
  // Useless oracle call for nested call testing
  int oracle_id = (*oracle_get_id)();
  (*oracle_getter)(oracle_id, "-?[01]");

  int file = (*fs_open)(filename, flags);
  if (file < 0) {
    *fd = -999;
    return -1;
  }
  *fd = file;
  return 0;
}

/*
 * Deletes a file by path. Returns 0 on success and -2 on failure.
 */
int file_unlink(char *filename) {
  // Useless oracle call for nested call testing
  int oracle_id = (*oracle_get_id)();
  (*oracle_getter)(oracle_id, "-?[02]");

  int fd;
  if (file_open(&fd, filename, O_RDWR) < 0) {
    return -2;
  }
  return (*fs_unlink)(filename);
}

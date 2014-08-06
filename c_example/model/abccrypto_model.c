#include <stdio.h>

// Previously retrieved random ints
int previous[64];
int prev_index = 0;

/*
 * Returns a random int between 0-255
 */
int get_new_random(int (oracle_getter)(char*)) {
  // Get random int
  int num = (*oracle_getter)("^<RANGE 0, 255>$");

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
int file_open(int *fd, char *filename, int flags, int (fs_open)(char*, int)) {
  int file = (*fs_open)(filename, flags);
  if (file < 0) {
    *fd = -999;
    return -1;
  }
  *fd = file;
  return 0;
}

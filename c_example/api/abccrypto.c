#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <fcntl.h>
#include "abctrace.h"

// Previously retrieved random ints
int previous[64];
int prev_index = 0;

// Whether rand has been seeded
short rand_is_seeded = 0;

/*
 * Returns a random int between 0-255
 */
int get_new_random_(void) {
  // Seed rand if it hasn't been already
  if (!rand_is_seeded) {
    srand((unsigned) time(NULL));
    rand_is_seeded = 1;
  }

  // Get random int
  int num = rand() % 256;

  // Store random int for later calls to get_prior_random(), and return
  previous[prev_index++] = num;
  return num;
}

// CHECKAPI SHIM FOR LOGGING
int get_new_random(void) {
  int ret = get_new_random_();
  write_type_and_func("int", "get_new_random");
  write_return_int(ret);
  return ret;
}

/*
 * Returns a previously retrieved random int. If index is negative, returns -1.
 * If index is >= the number of random ints previously retrieved, returns -2.
 */
int get_prior_random_(int index) {
  // Negative index
  if (index < 0) {
    return -1;
  // Index out of bounds
  } else if (index >= prev_index) {
    return -2;
  }

  return previous[index];
}

// CHECKAPI SHIM FOR LOGGING
int get_prior_random(int index) {
  int ret = get_prior_random_(index);
  write_type_and_func("int", "get_prior_random");
  write_int(index);
  write_return_int(ret);
  return ret;
}

/*
 * Opens a file, placing the file descriptor in fd. On success, returns 0. On
 * failure, returns -1.
 */
int file_open_(int *fd, char *filename, int flags) {
  int file = open(filename, flags);
  if (file < 0) {
    *fd = -999;
    return -1;
  }
  *fd = file;
  return 0;
}

// CHECKAPI SHIM FOR LOGGING
int file_open(int *fd, char *filename, int flags) {
  int ret = file_open_(fd, filename, flags);
  write_type_and_func("int", "file_open");
  write_int_ret_arg(*fd);
  write_string(filename);
  write_int(flags);
  write_return_int(ret);
  return ret;
}

/*
 */
int file_write(int fd, char *data, int *nbytes) {
  return 0;
}

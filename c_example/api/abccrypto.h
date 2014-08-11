/*
 * Returns a random int between 0-255
 */
int get_new_random(void);

/*
 * Returns a previously retrieved random int. If index is negative, returns -1.
 * If index is >= the number of random ints previously retrieved, returns -2.
 */
int get_prior_random(int index);

/*
 * Opens a file, placing the file descriptor in fd. On success, returns 0. On
 * failure, returns -1.
 */
int file_open(int *fd, char *filename, int flags);

/*
 * Deletes a file by path. Returns 0 on success and -1 on failure.
 */
int file_unlink(char *filename);

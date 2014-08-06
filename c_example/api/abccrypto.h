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
 */
int file_open(int *fd, char *filename, int flags);

/*
 */
int file_write(int fd, char *data, int *nbytes);

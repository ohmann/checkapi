#include <stdio.h>
#include <fcntl.h>
#include "abccrypto.h"

int main(void) {
  int i;
  for (i = 0; i < 10; i++)
    printf("%d\t", get_new_random());
  printf("\n");
  printf("%d\t\t\t%d\t\t\t%d\t\t\t%d", get_prior_random(0), get_prior_random(3), get_prior_random(6), get_prior_random(9));
  printf("\n");
  printf("(-1) = %d\n", get_prior_random(-1));
  printf("(10) = %d\n", get_prior_random(10));

  int fd;
  char *fileso[] = {"./abc.ERR", "aaa", "aaa", "api/abc.log"};
  int flags[] = {O_CREAT, O_RDWR, O_CREAT, O_RDWR};
  for (i = 0; i < sizeof(fileso) / sizeof(char*); i++) {
    int ret = file_open(&fd, fileso[i], flags[i]);
    printf("file_open(%s, %d) = %d, %d\n", fileso[i], flags[i], ret, fd);
  }


  char *filesu[] = {"aaa", "aaa", "bbb"};
  for (i = 0; i < sizeof(filesu) / sizeof(char*); i++) {
    int ret = file_unlink(filesu[i]);
    printf("file_unlink(%s) = %d\n", filesu[i], ret);
  }
  return 0;
}

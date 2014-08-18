#include <stdio.h>
#include "aprtrace.h"

#define LOGNAME "/home/ohmann/dev/checkapi.git/apr_checkapi/apr.log"
static FILE *out;
//static int first_run = 1;

void open_log() {
  //if (first_run) {
    //out = fopen(LOGNAME, "w");
    //first_run = 0;
  //} else {
    out = fopen(LOGNAME, "a");
  //}
}

void write_type_and_func(const char *type, const char *func, const int is_direct) {
  open_log();
  char *directflag = (is_direct == DIRECT ? "direct" : "nested");
  fprintf(out, "=== %s %s %s\n", type, func, directflag);
}

void write_int(const int i) {
  fprintf(out, "int %d\n", i);
}

void write_int_ret_arg(const int i) {
  fprintf(out, "int_retarg %d\n", i);
}

void write_char(const char c) {
  fprintf(out, "str %c\n", c);
}

void write_char_ret_arg(const char c) {
  fprintf(out, "str_retarg %c\n", c);
}

void write_string(const char *s) {
  fprintf(out, "str %s\n", s);
}

void write_string_ret_arg(const char *s) {
  fprintf(out, "str_retarg %s\n", s);
}

void write_return_int(const int i) {
  fprintf(out, "int_return %d\n", i);
  fclose(out);
}

void write_return_string(const char *s) {
  fprintf(out, "str_return %s\n", s);
  fclose(out);
}

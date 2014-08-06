#include <stdio.h>
#include "abctrace.h"

#define LOGNAME "abc.log"
static FILE *out;
static int first_run = 1;

void open_log() {
  if (first_run) {
    out = fopen(LOGNAME, "w");
    first_run = 0;
  } else {
    out = fopen(LOGNAME, "a");
  }
}

void write_type_and_func(char *type, char *func) {
  open_log();
  fprintf(out, "=== %s %s\n", type, func);
}

void write_int(int i) {
  fprintf(out, "int %d\n", i);
}

void write_int_ret_arg(int i) {
  fprintf(out, "int_retarg %d\n", i);
}

void write_string(char *s) {
  fprintf(out, "str %s\n", s);
}

void write_string_ret_arg(char *s) {
  fprintf(out, "str_retarg %s\n", s);
}

void write_return_int(int i) {
  fprintf(out, "int_return %d\n", i);
  fclose(out);
}

void write_return_string(char *s) {
  fprintf(out, "str_return %s\n", s);
  fclose(out);
}

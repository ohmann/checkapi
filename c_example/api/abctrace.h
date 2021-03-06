#ifndef ABCTRACE_H_
#define ABCTRACE_H_

#define DIRECT 1
#define NESTED 0

void write_type_and_func(char *type, char *func, int is_direct);
void write_int(int i);
void write_int_ret_arg(int i);
void write_string(char *s);
void write_string_ret_arg(char *s);
void write_return_int(int i);
void write_return_string(char *s);

#endif

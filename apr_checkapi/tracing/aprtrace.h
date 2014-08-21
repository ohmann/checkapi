#ifndef ABCTRACE_H_
#define ABCTRACE_H_

#define DIRECT 1
#define NESTED 0

// Must parallel defines in checkapicommon.h and framework.checkapi_globals.py
#define NULLINT -9999
#define NULLSTR "<NULL>"

void write_type_and_func(const char *type, const char *func, const int is_direct);
void write_int(const int i);
void write_int_ret_arg(const int i);
void write_char(const char c);
void write_char_ret_arg(const char c);
void write_string(const char *s);
void write_string_ret_arg(const char *s);
void write_return_int(const int i);
void write_return_string(const char *s);

#endif

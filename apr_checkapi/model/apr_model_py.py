"""
Python wrapper for APR file I/O model functions in model_src/file_io/unix/
"""

import os
from ctypes import *
from framework.checkapi_oracle_setter_getter import *
from framework.checkapi_exceptions import *
from framework.checkapi_files import *
from framework.checkapi_errno import *

cwd = os.path.dirname(__file__)
apr = CDLL(cwd + '/model_src/.libs/libapr-1.so')

# C function wrappers for CheckAPI python functions
# Oracle functions
oraclegetid_py = CFUNCTYPE(c_int)(oracle_get_id)
oraclegetter_py = CFUNCTYPE(c_int, c_int, c_char_p)(oracle_getter)
# File functions
fsfcntl2_py = CFUNCTYPE(c_int, c_int, c_int)(fs_fcntl)
fsfcntl3_py = CFUNCTYPE(c_int, c_int, c_int, c_int)(fs_fcntl)
fsopen_py = CFUNCTYPE(c_int, c_char_p, c_int, c_int)(fs_open)
fsclose_py = CFUNCTYPE(c_int, c_int)(fs_close)
fsunlink_py = CFUNCTYPE(c_int, c_char_p)(fs_unlink)
# Errno functions
seterrno_py = CFUNCTYPE(None, c_int)(set_errno)
geterrno_py = CFUNCTYPE(c_int)(get_errno)

def set_py_functions_model():
  apr.set_py_functions(oraclegetid_py, oraclegetter_py, fsfcntl2_py,
                       fsfcntl3_py, fsopen_py, fsclose_py, fsunlink_py,
                       seterrno_py, geterrno_py)

def apr_file_open_model(fd, fname, flag, perm):
  fd_c = c_int(fd)
  result = apr.apr_file_open_model(byref(fd_c), c_char_p(fname), flag, perm)
  return [fd_c.value, result]

def apr_file_close_model(fd):
  result = apr.apr_file_close_model(fd)
  return [result]

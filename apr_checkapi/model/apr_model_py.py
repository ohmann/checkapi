"""
Python wrapper for APR file I/O model functions in model_src/file_io/unix/
"""

import os
from ctypes import *
from framework.checkapi_oracle_setter_getter import *
from framework.checkapi_exceptions import *
from framework.checkapi_files import *

cwd = os.path.dirname(__file__)
apr = CDLL(cwd + '/model_src/.libs/libapr-1.so', use_errno=True)

# C function wrappers for CheckAPI python functions
oraclegetid_py = CFUNCTYPE(c_int)(oracle_get_id)
oraclegetter_py = CFUNCTYPE(c_int, c_int, c_char_p)(oracle_getter)
fsfcntl2_py = CFUNCTYPE(c_int, c_int, c_int)(fs_fcntl)
fsfcntl3_py = CFUNCTYPE(c_int, c_int, c_int, c_int)(fs_fcntl)
fsopen_py = CFUNCTYPE(c_int, c_char_p, c_int, c_int)(fs_open)
fsunlink_py = CFUNCTYPE(c_int, c_char_p)(fs_unlink)

def set_py_functions_model():
  apr.set_py_functions(oraclegetid_py, oraclegetter_py, fsfcntl2_py,
                       fsfcntl3_py, fsopen_py, fsunlink_py)

def apr_file_open_model(fd, fname, flag, perm):
  fd_c = c_int(fd)
  result = apr.apr_file_open_model(byref(fd_c), c_char_p(fname), flag, perm)
  return [fd_c.value, result]

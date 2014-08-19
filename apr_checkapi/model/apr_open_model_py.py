"""
Python wrapper model_src/file_io/unix/open.c
"""

import os
from ctypes import *
from framework.checkapi_oracle_setter_getter import *
from framework.checkapi_exceptions import *
from framework.checkapi_files import *

cwd = os.path.dirname(__file__)
apr_open = CDLL(cwd + '/model_src/.libs/libapr-1.so')

# C function wrappers for CheckAPI python functions
oraclegetid_py = CFUNCTYPE(c_int)(oracle_get_id)
oraclegetter_py = CFUNCTYPE(c_int, c_int, c_char_p)(oracle_getter)
fsopen_py = CFUNCTYPE(c_int, c_char_p, c_int)(fs_open)
fsunlink_py = CFUNCTYPE(c_int, c_char_p)(fs_unlink)

def set_py_functions_model():
  apr_open.set_py_functions(oraclegetid_py, oraclegetter_py, fsopen_py,
    fsunlink_py)

def apr_file_open_model(newf, fname, flag, perm):
  newf_c = c_int(newf)
  result = apr_open.apr_file_open(byref(newf_c), c_char_p(fname), flag, perm)
  return [newf_c.value, result]

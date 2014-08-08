"""
Python wrapper for abccrypto_model.c
"""

import os
from ctypes import *
from framework.checkapi_oracle_setter_getter import *
from framework.checkapi_exceptions import *
from framework.checkapi_files import *

cwd = os.path.dirname(__file__)
abccrypto = CDLL(cwd + '/abccrypto_model.so')

# C function wrappers for CheckAPI python functions
oraclegetid_py = CFUNCTYPE(c_int)(oracle_get_id)
oraclegetter_py = CFUNCTYPE(c_int, c_int, c_char_p)(oracle_getter)
fsopen_py = CFUNCTYPE(c_int, c_char_p, c_int)(fs_open)

def get_new_random_model():
  result = abccrypto.get_new_random(oraclegetid_py, oraclegetter_py)
  return [result]

def get_prior_random_model(index):
  result = abccrypto.get_prior_random(index)
  return [result]

def file_open_model(fd, filename, flags):
  fd_c = c_int(fd)
  result = abccrypto.file_open(byref(fd_c), c_char_p(filename), flags, fsopen_py)
  return [fd_c.value, result]

def file_write_model(fd, data, nbytes):
  result = abccrypto.file_write(fd, c_char_p(data), pointer(c_int(nbytes)))
  return [nbytes, result]

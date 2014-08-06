"""
Python wrapper for abccrypto_model.c
"""

from ctypes import *
from framework.checkapi_oracle_setter_getter import *
from framework.checkapi_exceptions import *
from framework.checkapi_files import *

abccrypto = CDLL('/home/ohmann/dev/checkapi/c_example/model/abccrypto_model.so')

# C function wrappers for CheckAPI python functions
oraclegetter_py = CFUNCTYPE(c_int, c_char_p)(oracle_getter)
fsopen_py = CFUNCTYPE(c_int, c_char_p, c_int)(fs_open)

def get_new_random_model():
  result = abccrypto.get_new_random(oraclegetter_py)
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

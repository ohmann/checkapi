"""
APR and other C constants and macros used in CheckAPI's emulated file system and
open files state
"""

# fcntl cmd types
F_GETFD = 1
F_SETFD = 2

# File flags for open and others
O_CREAT = 64
O_EXCL = 128
O_CLOEXEC = 524288

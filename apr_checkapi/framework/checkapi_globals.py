'''
Globals that are used throughout CheckAPI
'''

# Whether to output debugging statements while verifying or parsing, or about
# the emulated fs and open files state
debugverify = False
debugparse = False
debugfs = False

# The model's current working directory
workingdir = "/"

# Must parallel defines in aprtrace.h and checkapicommon.h
NULLINT = -9999

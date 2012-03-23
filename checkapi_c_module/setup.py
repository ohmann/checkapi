#! /usr/bin/env python
# The original is from uppir project, created by Justin Cappos

from distutils.core import setup, Extension

import sys

print "This setup.py script is not intended to be used for installation.  It"
print "is only constructed to build the C CheckAPI interposition. There will be" 
print "a serious version of this written later that has the usual functionality."

# Must have Python >= 2.5 and < 3.0.   If Python version == 2.5.X, then
# simplejson is required.
if sys.version_info[0] != 2 or sys.version_info[1] < 5:
  print "Requires Python >= 2.5 and < 3.0"
  sys.exit(1)

# We need a json library.   (We'll use the standard library json in Python 2.6 
# and greater...
if sys.version_info[1] == 5:
  try:
    import simplejson
  except ImportError:
    print "The package simplejson is required on Python 2.5.X"
    print "You can try to use easy_install to get this package or download"
    print "and install from source."
    sys.exit(1)


checkapi_interposition_c = Extension("checkapi_interposition",sources=["checkapi_interposition.c"])

setup(	name="CheckAPI",
    version="0.0-prealpha",
    ext_modules=[checkapi_interposition_c],
    description="""An early version of CheckAPI with a simple C-based interposition.""",
    author="Jerome Yang Li",
    author_email="yli28@students.poly.edu",
)



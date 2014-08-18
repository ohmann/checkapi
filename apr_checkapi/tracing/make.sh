#!/bin/bash

#export LD_LIBRARY_PATH=/home/ohmann/dev/checkapi.git/apr_checkapi/tracing:$LD_LIBRARY_PATH
#gcc -Wall -c -Wl,-soname,aprtrace -o libaprtrace.so -fPIC aprtrace.c

# If header has changed, update it in APR's include dir
cp -u aprtrace.h ../apr_src/include/aprtrace.h

# Compile static '.a' library
gcc -Wall -c -o aprtrace.o -fPIC aprtrace.c
ar rcs libaprtrace.a aprtrace.o

#!/bin/bash

echo "========================================================="
echo "================== Compiling APR model =================="

cd model
# If CheckAPI common header has changed, update it in the APR model include dir
cp -u checkapicommon.h model_src/include/checkapicommon.h

# Compile static '.a' for CheckAPI common library
gcc -Wall -c -o checkapicommon.o -fPIC checkapicommon.c
ar rcs libcheckapicommon.a checkapicommon.o

cd model_src
# Make the APR model itself
./configure --disable-threads
make

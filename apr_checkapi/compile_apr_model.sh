#!/bin/bash

echo "========================================================="
echo "================== Compiling APR model =================="

cd model/model_src
# Make the APR model itself
./configure --disable-threads
make

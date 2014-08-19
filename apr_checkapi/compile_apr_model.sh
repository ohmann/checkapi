#!/bin/bash

echo "========================================================="
echo "================== Compiling APR model =================="
cd model/model_src

./configure --disable-threads
make

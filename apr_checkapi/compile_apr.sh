#!/bin/bash

echo "========================================================="
echo "===================== Compiling APR ====================="
cd apr_src

./configure --disable-threads
make

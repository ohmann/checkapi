#!/bin/bash

# Compiles the APR tracing library, compiles APR, and runs all file i/o tests to
# generate traces in apr.log

cd tracing
./make.sh

cd ..
./compile_apr.sh

./run_fileiotests.sh

#!/bin/bash

# Compiles the APR tracing library, compiles APR, runs all file i/o tests to
# generate traces in apr.log, and finally compiles APR model

cd tracing
./make.sh

cd ..
./compile_apr.sh

./run_fileiotests.sh

./compile_apr_model.sh

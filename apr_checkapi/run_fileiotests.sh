#!/bin/bash

echo "========================================================="
echo "============== Running APR file i/o tests ==============="
cd apr_src/test

# Clear old log
cat /dev/null > ../../apr.log

# Make and run file i/o tests
make
./testall testdir testdup testfile testfilecopy testflock testlfs testpipe testtemp

#!/bin/bash

cd api
gcc -shared -Wall -Wl,-soname,abccrypto -o abccrypto.so -fPIC abccrypto.c abctrace.c
gcc -Wall -o abctest abctest.c abccrypto.c abctrace.c

cd ../model
gcc -shared -Wall -Wl,-soname,abccrypto_model -o abccrypto_model.so -fPIC abccrypto_model.c

#!/bin/bash

rm -rf build
python setup.py build
cp build/lib.linux-x86_64-2.6/checkapi_interposition.so ./
rm -rf build

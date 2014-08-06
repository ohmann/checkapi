#!/bin/bash

rm -f abc.ERR

./api/abctest
mv abc.log ./api/

rm -f abc.ERR

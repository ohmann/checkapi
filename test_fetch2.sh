#!/bin/bash

for TRY in {1..1000}
do
    curl http://128.238.64.142:12345/ > /dev/null 2>/dev/null
done


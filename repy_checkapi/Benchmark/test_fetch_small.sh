#!/bin/bash

for TRY in {1..10}
do
    curl http://127.0.0.1:12345/ > /dev/null 2>/dev/null
done


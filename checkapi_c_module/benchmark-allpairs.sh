#!/bin/bash
# Used to automate benchmarking

# Command to run for seclayer
SEC_CMD="python repy.py restrictions.full encasementlib.repy"
NORM_CMD="python repy.py restrictions.full"
SEC_LAYERS="all-logsec.py ip-seclayer.py forensiclog.repy"
SERVER="dylink.repy librepy.repy allpairspingv2.repy 12345"

# Kill all python instances
echo "Killing python"
killall -9 python Python >/dev/null 2>&1

# CPU benchmarks
echo
echo "####"
echo "AllPairsPing test"
echo "####"
for LAYER in $SEC_LAYERS
do
   echo 
   echo "Layer: $LAYER"
   for iter in {1}
   do
       $SEC_CMD $LAYER $SERVER &
       PID=$!
       sleep 4
       for i in {1..10}
       do
           { time ./test_fetch2.sh; } 2>&1 | grep real | sed -e 's|^.*0m\([0-9.]*s\)$|\1|' -e 's|s||'
       done
       kill -9 $PID
       wait $PID
   done
done
# Do the no security now
echo

echo "Layer: No security"
for iter in {1}
do
    $NORM_CMD $SERVER &
    PID=$!
    sleep 4
    for i in {1..10}
    do
        { time ./test_fetch2.sh; } 2>&1 | grep real | sed -e 's|^.*0m\([0-9.]*s\)$|\1|' -e 's|s||'
    done
    kill -9 $PID
    wait $PID
done

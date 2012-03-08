#!/bin/bash
# Used to automate benchmarking

# The types of tests
TESTS="webserver webserver-inmem webserver-inmem2 webserver-file webserver-listfiles webserver-load"
TESTS="webserver-listfiles"

# Command to run for seclayer
SEC_CMD="python repy.py restrictions.full encasementlib.repy"
NORM_CMD="python repy.py restrictions.full"
SEC_LAYERS="all-logsec.py ip-seclayer.py forensiclog.repy"
SERVER="dylink.repy librepy.repy "

# Kill all python instances
echo "Killing python"
killall -9 python Python >/dev/null 2>&1

# CPU benchmarks
for TEST in $TESTS
do
    # Do the tests with the layers
    for LAYER in $SEC_LAYERS
    do
       echo 
       echo "Layer: $LAYER"
       for iter in {1}
       do  
           echo $SEC_CMD $LAYER $SERVER$TEST.repy 
           $SEC_CMD $LAYER $SERVER$TEST.repy &
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
        echo $NORM_CMD $SERVER$TEST.repy 
        $NORM_CMD $SERVER$TEST.repy &
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


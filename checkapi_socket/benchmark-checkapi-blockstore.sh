#!/bin/bash
# Used to automate benchmarking
TEST="blockstore"

# Command to run for seclayer
SEC_CMD="python repy.py restrictions.full"
SERVER="dylink.repy check_api.repy librepy.repy blockstore.py test_benchmark 12345"
CHECKAPIVERIFY="python repy.py restrictions.full dylink.repy check_api_verify.repy"


echo
echo "##############################"
echo "$TEST test"
echo "##############################"
echo

for iter in {1}
do
    # Kill all python instances
    killall -9 python Python >/dev/null 2>&1

    # Start Verification Process
    echo "Lanuch Verification  Command: $CHECKAPIVERIFY"
    $CHECKAPIVERIFY &

    # Wait for Verification process start
    sleep 2

    # Get the start time of Interposition
    time1=`date`	

    # Start Interposition Process
    echo "Lanuch Interposition Command: $SEC_CMD $SERVER"
    $SEC_CMD $SERVER >/dev/null 2>&1 &
    PID=$!

    # Wait for Interpostion process start
    sleep 10

    # Start Test Script
    for i in {1..10}
    do
        { time ./test_blockstore_fetch.sh; } 2>&1 | grep real | sed -e 's|^.*0m\([0-9.]*s\)$|\1|' -e 's|s||'
    done

    # Test fininshed. Kill Interposition process
    kill -9 $PID
    wait $PID

    # Get the finish time of Interposition
    time2=`date`

    # Print Interposition running time
    echo "CheckAPI Interposition Start  Time: $time1"
    echo "CheckAPI Interposition Finish Time: $time2"

done


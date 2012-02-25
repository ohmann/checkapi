#!/bin/bash
# Used to automate benchmarking

# Command to run for seclayer
SEC_CMD="python repy.py restrictions.full encasementlib.repy"
SERVER="dylink.repy check_api.repy librepy.repy allpairspingv2.repy 12345"
CHECKAPIVERIFY="python repy.py restrictions.full dylink.repy check_api_verify.repy"


# Kill all python instances
echo "Killing python"
killall -9 python Python >/dev/null 2>&1

# CheckAPI
echo
echo "@@@@@@@@@@@@@@@@@@@@@@@@@@"
echo "Layer: check_api"
echo "@@@@@@@@@@@@@@@@@@@@@@@@@@"

for iter in {1}
do
    # Start Verification Process
    echo $CHECKAPIVERIFY
    $CHECKAPIVERIFY &
    sleep 3

    # Start Interposition Process
    echo $SEC_CMD $SERVER 
    $SEC_CMD $SERVER &
    PID=$!
    sleep 10

    for i in {1..10}
    do
        { time ./test_fetch2.sh; } 2>&1 | grep real | sed -e 's|^.*0m\([0-9.]*s\)$|\1|' -e 's|s||'
    done

    sleep 1
    kill -9 $PID
done

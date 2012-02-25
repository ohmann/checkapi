#!/bin/bash
# Used to automate benchmarking
TEST="Block Store Server in CheckAPI"

# Command to run for seclayer
SEC_CMD="python repy.py restrictions.full encasementlib.repy"
SERVER="dylink.repy check_api.repy librepy.repy blockstore.py test_benchmark 12345"
CHECKAPIVERIFY="python repy.py restrictions.full dylink.repy check_api_verify.repy"


echo
echo "####"
echo "$TEST"
echo "####"

echo 
for iter in {1}
do
    # Kill all python instances
    echo "Killing python"
    killall -9 python Python >/dev/null 2>&1

    echo $CHECKAPIVERIFY
    $CHECKAPIVERIFY &
    sleep 2

    echo $SEC_CMD $SERVER
    $SEC_CMD $SERVER >/dev/null 2>&1 &
    PID=$!

    sleep 10
    for i in {1..10}
    do
        { time ./test_blockstore_fetch.sh; } 2>&1 | grep real | sed -e 's|^.*0m\([0-9.]*s\)$|\1|' -e 's|s||'
    done
    kill -9 $PID
    wait $PID
done


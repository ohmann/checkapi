#!/bin/bash
# Used to automate benchmarking
TEST="richard"

# Command to run for seclayer
SEC_CMD="python repy.py restrictions.full"
SERVER="dylink.repy check_api.repy richards.repy 30"
CHECKAPI_VERIFY="python repy.py restrictions.full dylink.repy check_api_verify.repy"


echo
echo "##############################"
echo "$TEST test"
echo "##############################"
echo

for i in {1..10}
do
    # Kill all python instances
    killall -9 python Python >/dev/null 2>&1

    # Start Verification Process
    echo "Lanuch Verification  Command: $CHECKAPI_VERIFY"
    $CHECKAPI_VERIFY &
    
    # Wait for Verification process start
    sleep 2

    # Start Interposition Process
    echo "Lanuch Interposition Command: $SEC_CMD $SERVER"
    $SEC_CMD $SERVER | grep "Average" | perl -pe "s/[a-zA-Z: ]*([0-9.]+) ms/\1/"

    echo "-------------------------------------------------------"
    echo 
done


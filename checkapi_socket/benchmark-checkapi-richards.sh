#!/bin/bash
# Used to automate benchmarking

# Command to run for seclayer
SEC_CMD="python repy.py restrictions.full encasementlib.repy"
CHECKAPI_VERIFY="python repy.py restrictions.full dylink.repy check_api_verify.repy"

CHECKAPI="dylink.repy check_api.repy"
SERVER="richards.repy 30"


for i in {1..10}
do
    # Kill all python instances
    #echo "Killing python"
    echo 
    echo $i
    killall -9 python Python >/dev/null 2>&1

    echo $CHECKAPI_VERIFY
    $CHECKAPI_VERIFY &
    
    sleep 5
    echo $SEC_CMD $CHECKAPI $SERVER
    $SEC_CMD $CHECKAPI $SERVER | grep "Average" | perl -pe "s/[a-zA-Z: ]*([0-9.]+) ms/\1/"
done


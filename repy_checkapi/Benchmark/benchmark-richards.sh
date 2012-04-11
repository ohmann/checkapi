#!/bin/bash
# Used to automate benchmarking

# The types of tests
#TESTS="inmem inmem2 file listfiles load uptime"
#TESTS="inmem2"

# Command to run for seclayer
SEC_CMD="python repy.py restrictions.full encasementlib.repy"
NORM_CMD="python repy.py restrictions.full"
SEC_LAYERS="all-logsec.py ip-seclayer.py forensiclog.repy"
SERVER="richards.repy 30"

# Kill all python instances
echo "Killing python"
killall -9 python Python >/dev/null 2>&1

echo
echo "####"
echo "Richards test"
echo "####"
for LAYER in $SEC_LAYERS
do
   echo 
   echo "Layer: $LAYER"
   for i in {1..10}
   do
       $SEC_CMD $LAYER $SERVER | grep "Average" | perl -pe "s/[a-zA-Z: ]*([0-9.]+) ms/\1/"
   done
done

# Do the no security now
echo
echo "Layer: No security"

for i in {1..10}
do
    $NORM_CMD $SERVER | grep "Average" | perl -pe "s/[a-zA-Z: ]*([0-9.]+) ms/\1/"
done


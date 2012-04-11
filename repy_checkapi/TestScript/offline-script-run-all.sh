#!/bin/bash
# Used to automate benchmarking

#benchmarks="benchmark-checkapi-blockstore"
benchmarks="benchmark-checkapi-allpairsping benchmark-checkapi-blockstore benchmark-checkapi-webserver benchmark-checkapi-webserver-meg"
testcases="Testcase04"

TEST_SCRIPT_NAME="benchmark-checkapi-allpairsping"
SOURCE_FOLDER="../$TEST_SCRIPT_NAME"
OFFLINE_TEST_SCRIPT="python repy.py restrictions.full dylink.repy check_api_offline_verify.repy"


for testcase in $testcases
do 
    echo "------------------------------------"
    echo "Testcase: $testcase"
    echo "------------------------------------"

    killall -9 python

    #echo ../$testcase-$benchmark
    rm -rf ../$testcase
    mkdir ../$testcase

    \cp -rf ../Repy_Env/* ../$testcase
    \cp -rf ../CheckAPI/* ../$testcase
    \cp -rf ../Benchmark/* ../$testcase
    \cp -rf ../TestScript/Testcase/$testcase/* ../$testcase

    cd ../$testcase

    for benchmark in $benchmarks 
    do
        echo "------------------------------------"
        echo "Generate log file: $benchmark"
        echo "------------------------------------"

        rm -rf ../TestScript/$testcase-$benchmark
        mkdir ../TestScript/$testcase-$benchmark

        rm -rf *.output
        ./$benchmark.sh
        sleep 5

        for test in {1..10}
	do
    	    echo "------------------------------------"
            echo "Test Time: $test"
            echo "------------------------------------"

            ../TestScript/offline-usage-interposition.sh > ../TestScript/$testcase-$benchmark/usage_$test.log &
            PID=$!

            echo $OFFLINE_TEST_SCRIPT
            # Get the start time of Interposition
            time1=`date`
            time $OFFLINE_TEST_SCRIPT
            # Get the finish time of Interposition
            time2=`date`

            # Print Interposition running time
            echo "CheckAPI Interposition Start  Time: $time1"
            echo "CheckAPI Interposition Finish Time: $time2"            

            sleep 2
            kill -9 $PID

        done
        echo "-------------------------------------------"
         
        killall -9 python
    done
done


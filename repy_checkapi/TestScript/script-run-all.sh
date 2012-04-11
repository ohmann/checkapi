#!/bin/bash
# Used to automate benchmarking

benchmarks="benchmark-checkapi-allpairsping benchmark-checkapi-blockstore benchmark-checkapi-webserver benchmark-checkapi-webserver-meg"
testcases="Testcase01 Testcase02 Testcase03"

TEST_SCRIPT_NAME="benchmark-checkapi-allpairsping"
SOURCE_FOLDER="../$TEST_SCRIPT_NAME"
        

for testcase in $testcases
do 
    echo "------------------------------------"
    echo "Testcase: $testcase"
    echo "------------------------------------"

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
        echo "Benchmark: $benchmark"
        echo "------------------------------------"

        rm -rf ../TestScript/$testcase-$benchmark
        mkdir ../TestScript/$testcase-$benchmark

	for test in {1..10}
	do
    	    echo "------------------------------------"
            echo "Test Time: $test"
            echo "------------------------------------"

            ../TestScript/usage-interposition.sh > ../TestScript/$testcase-$benchmark/usage_$test.log &
            PID=$!

            echo ./$benchmark.sh
            ./$benchmark.sh
            sleep 2
            kill -9 $PID
        done
        echo "-------------------------------------------"
    done
done


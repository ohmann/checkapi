rm -rf benchmark-allpairs-checkapi-usage-verification.log
rm -rf benchmark-allpairs-checkapi-usage-interposition.log

while true
do
    ps aux |grep python | grep check_api_verify | grep '[RS]l' | awk '{print $3 "\t " $6}' 2>&1 | tee -a benchmark-allpairs-checkapi-usage-verification.log
    ps aux |grep python | grep allpairspingv | grep '[RS]l' | awk '{print $3 "\t " $6}' 2>&1 | tee -a benchmark-allpairs-checkapi-usage-interposition.log
    sleep "1"
    echo "-----------------"
done

#allpairspingv2
#advertiseserver
#blockstore
#webserver
#richards

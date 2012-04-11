while true
do
    ps aux |grep python | grep check_api_offline_verify.repy | grep '[RS]l' | awk '{print $3 "\t " $6}'
    sleep "1"
done


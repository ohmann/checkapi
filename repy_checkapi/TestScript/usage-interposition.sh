while true
do
    ps aux |grep python | grep check_api.repy | grep '[RS]l' | awk '{print $3 "\t " $6}'
    sleep "1"
done


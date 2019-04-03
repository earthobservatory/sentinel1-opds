python2 cron-updatelist.py "2015-07-01T00:00:00.000Z" "2016-01-02T00:00:00.000Z"
wait
echo '2015S2 is finished'
python2 cron-updatelist.py "2016-01-01T00:00:00.000Z" "2016-07-02T00:00:00.000Z"
wait
echo '2016S1 is finished'
python2 cron-updatelist.py "2016-07-01T00:00:00.000Z" "2017-01-02T00:00:00.000Z"
wait
echo '2016S2 is finished'
python2 cron-updatelist.py "2017-01-01T00:00:00.000Z" "2017-07-02T00:00:00.000Z"
wait
echo '2017S1 is finished'
python2 cron-updatelist.py "2017-07-01T00:00:00.000Z" "2018-01-02T00:00:00.000Z"
wait
echo '2017S2 is finished'
python2 cron-updatelist.py "2018-01-01T00:00:00.000Z" "2018-07-02T00:00:00.000Z"
wait
echo '2018S1 is finished'
python2 cron-updatelist.py "2018-07-01T00:00:00.000Z" "2019-01-02T00:00:00.000Z"
wait
echo '2018S2 is finished'

#! /bin/sh

if [ $# -ne 1 ]; then
    echo "指定された引数は$#個です。" 1>&2
    echo "実行するには1個の引数が必要です。" 1>&2
    exit 1
fi

if [ $1 = 'stop' -o $1 = 'restart' ]; then
    echo 'stop'
    ps aux | grep -v grep | grep python3 | grep smart_speaker.py | awk '{ print "kill -KILL", $2 }' | sh
    ps aux | grep -v grep | grep python3 | grep smart_speaker.py | awk '{ print "kill -KILL", $2 }' | sh
fi

if [ $1 = 'check' -o $1 = 'stop' -o $1 = 'restart' ]; then
    echo 'check 1'
    ps aux | grep python3
    echo 'check 2'
    ps aux | grep -v grep | grep python3
fi

if [ $1 = 'start' -o $1 = 'restart' ]; then
    echo 'start'
    nohup python3 smart_speaker.py >/dev/null 2>&1 </dev/null &
fi

if [ $1 = 'test' ]; then
    echo 'test'
    python3 smart_speaker.py
fi



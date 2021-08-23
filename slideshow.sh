#!/bin/bash
while true
do
    fbi --vt 1 --autozoom --timeout 5 --device /dev/fb0 --noreadahead --cachemem 0 --noverbose --norandom /home/umbrel/umbrel-crypto-display/images/* > /dev/null 2>&1
    sleep 120
    killall fbi > /dev/null 2>&1
done

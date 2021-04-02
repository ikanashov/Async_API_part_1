#!/bin/sh

python etlproducer.py &
sleep 60
python etlconsumer.py &

while true; do echo 'eltworked '; date; sleep 120; done

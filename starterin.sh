#!/bin/bash 
forever start -a -l ./erin/logs/erin.log -e err.log -c python3 --sourceDir ./erin/src/ main.py
sleep 1
echo "DONE"

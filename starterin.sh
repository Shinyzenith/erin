#!/bin/bash 
forever start -a -l /home/aakash/erin/logs/erin.log -e err.log -c python3 --sourceDir /home/aakash/erin/src/ main.py
sleep 1
echo "DONE"
